import argparse
import json
import logging
import threading
import time

import kafka

import opl.args
import opl.db
import opl.generators.inventory_ingress
import opl.skelet

import psycopg2


def gen_and_send(args, status_data, payload_generator, producer, collect_info):
    def handle_send_success(*args, **kwargs):
        with kwargs["data_lock"]:
            kwargs["data_stats"]["successes"] += 1

    def handle_send_failure(*args, **kwargs):
        logging.error(f"Failed to send message {args}; {kwargs}")
        with kwargs["data_lock"]:
            kwargs["data_stats"]["failures"] += 1

    def wait_for_next_second():
        second = int(time.perf_counter())
        while second == int(time.perf_counter()):
            time.sleep(0.01)

    data_stats = {"successes": 0, "failures": 0}  # counting messages
    data_lock = threading.Lock()  # lock for messages counting

    in_second = 0  # how many messages we have sent in this second
    wait_for_next_second()
    this_second = int(time.perf_counter())  # second relevant for in_second

    logging.info("Started message generation")
    status_data.set_now("parameters.payload_generator.started_at")

    for mid, message in payload_generator:
        logging.debug(f"Processing message {mid}: {message}")

        # Add currently processed host to data
        if message["data"]["account"] not in collect_info["accounts"]:
            collect_info["accounts"][message["data"]["account"]] = []
        current_info = {
            "fqdn": message["data"]["fqdn"],
            "subscription_manager_id": message["data"]["subscription_manager_id"],
        }
        if "insights_id" in message["data"]:
            current_info["insights_id"] = message["data"]["insights_id"]
        collect_info["accounts"][message["data"]["account"]].append(current_info)

        value = json.dumps(message).encode()

        future = producer.send(args.kafka_topic, value=value)
        future.add_callback(
            handle_send_success, data_stats=data_stats, data_lock=data_lock
        )
        future.add_errback(
            handle_send_failure, data_stats=data_stats, data_lock=data_lock
        )

        # Limit producing rate to given value
        if int(time.perf_counter()) == this_second:
            in_second += 1
            if in_second == args.rate:
                logging.debug(f"In second {this_second} sent {in_second} messages")
                wait_for_next_second()
                this_second += 1
                in_second = 0
        else:
            if args.rate != 0 and args.rate != in_second:
                logging.warning(
                    f"In second {this_second} sent {in_second} messages (but wanted to send {args.rate})"
                )
                this_second = int(time.perf_counter())
                in_second = 0

    producer.flush()
    status_data.set_now("parameters.payload_generator.sent_at")

    # Make sure all messages were produced
    for i in range(10):
        if sum(data_stats.values()) == args.count:
            logging.info(f"Sent all {args.count} messages, great")
            break
        else:
            logging.debug(
                f"Sent {data_stats['successes']}&{data_stats['failures']} out of {args.count} messages, waiting"
            )
            time.sleep(1)

    logging.info("Finished message generation")
    status_data.set_now("parameters.payload_generator.ended_at")

    if data_stats["failures"] > 0:
        raise Exception(
            f"Failed to send {data_stats['failures']} messages out of totally requested {args.count}"
        )
    if sum(data_stats.values()) != args.count:
        raise Exception(
            f"Not all messages sent {data_stats['successes']} + {data_stats['failures']} != {args.count}"
        )


def verify(args, status_data, inventory, collect_info):
    # Generatate set of IDs to check in the DB
    remaining_ids = set()
    for a in collect_info["accounts"].values():
        for h in a:
            remaining_ids.add(h["subscription_manager_id"])
    logging.info(f"Going to verify {len(remaining_ids)} IDs")

    inventory_cursor = inventory.cursor()

    batch_size = 100  # how many IDs to check in one go
    attempt = 0
    attempts_max = (args.count // batch_size + 1) * 10
    while True:
        inventory_cursor.execute(
            """SELECT canonical_facts ->> 'subscription_manager_id'
               FROM hosts
               WHERE canonical_facts ->> 'subscription_manager_id'=ANY(%s)""",
            (list(remaining_ids)[:batch_size],),
        )
        existing_ids = set([i[0] for i in inventory_cursor.fetchall()])
        remaining_ids = remaining_ids - existing_ids

        # Are we done yet?
        if len(remaining_ids) == 0:
            logging.info("All IDs present in the Inventory DB")
            break

        # Are we out of attempts?
        attempt += 1
        if attempt > attempts_max:
            raise Exception(
                f"After {attempt} attempts, we still need to check {len(remaining_ids)} out of {args.count}"
            )

        # If there were no new hosts now, wait a bit
        if len(existing_ids) == 0:
            logging.debug(
                f"Waiting for IDs, attempt {attempt}, remaining {len(remaining_ids)}"
            )
            time.sleep(1)

    inventory_cursor.close()


def gen_send_verify(args, status_data):
    logging.info("Creating payload generation instance")
    payload_generator = opl.generators.inventory_ingress.InventoryIngressGenerator(
        count=args.count,
        relatives=args.relatives,
        packages=args.packages,
        template=args.template,
    )

    logging.info(f"Creating producer to {args.kafka_host}:{args.kafka_port}")
    producer = kafka.KafkaProducer(
        bootstrap_servers=[f"{args.kafka_host}:{args.kafka_port}"], api_version=(0, 10)
    )

    logging.info("Creating Inventory DB connection")
    inventory_db_conf = {
        "host": args.inventory_db_host,
        "port": args.inventory_db_port,
        "database": args.inventory_db_name,
        "user": args.inventory_db_user,
        "password": args.inventory_db_pass,
    }
    inventory = psycopg2.connect(**inventory_db_conf)

    logging.info("Creating data structure to store list of accounts and so")
    collect_info = {"accounts": {}}  # simplified info about hosts

    gen_and_send(
        args,
        status_data,
        payload_generator=payload_generator,
        producer=producer,
        collect_info=collect_info,
    )
    verify(
        args,
        status_data,
        inventory=inventory,
        collect_info=collect_info,
    )

    status_data.set("parameters.payload_generator.count", args.count)
    status_data.set("parameters.payload_generator.relatives", args.relatives)
    status_data.set("parameters.payload_generator.packages", args.packages)
    status_data.set("parameters.payload_generator.template", args.template)
    status_data.set("parameters.inventory_db", inventory_db_conf)

    logging.info(f"Dumping data to file {args.data_file}")
    with open(args.data_file, "w") as fp:
        json.dump(collect_info, fp, sort_keys=True, indent=4)


def populate_main():
    parser = argparse.ArgumentParser(
        description="Generate host-ingress messages, produce them to ingress topic and make sure they appear in DB",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--count", default=100, type=int, help="How many messages to prepare"
    )
    parser.add_argument(
        "--relatives",
        default=100,
        type=int,
        help="How many orgs/accounts should be in the generated hosts",
    )
    parser.add_argument(
        "--packages",
        default=500,
        type=int,
        help="How many packages addresses should each host have",
    )
    parser.add_argument(
        "--template",
        default="inventory_ingress_puptoo_template.json.j2",
        help="What message template to use (not implemented yet)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=0,
        help="How many messages per second should we produce (0 for no limit)",
    )
    parser.add_argument(
        "--kafka-topic",
        default="platform.inventory.host-ingress",
        help="Topic to produce to",
    )
    parser.add_argument(
        "--data-file",
        default="/tmp/data-file.json",
        help="Where to save list of accounts and so that were created",
    )
    opl.args.add_kafka_opts(parser)
    opl.args.add_inventory_db_opts(parser)

    with opl.skelet.test_setup(parser) as (args, status_data):
        gen_send_verify(args, status_data)


def cleanup(args, status_data):
    logging.info("Creating Inventory DB connection")
    inventory_db_conf = {
        "host": args.inventory_db_host,
        "port": args.inventory_db_port,
        "database": args.inventory_db_name,
        "user": args.inventory_db_user,
        "password": args.inventory_db_pass,
    }
    inventory = psycopg2.connect(**inventory_db_conf)

    inventory_cursor = inventory.cursor()

    logging.info("Truncating Inventory DB 'hosts' table")
    inventory_cursor.execute("TRUNCATE hosts")

    status_data.set_now("parameters.inventory_db.table_hosts.truncated_at")


def cleanup_main():
    parser = argparse.ArgumentParser(
        description="Truncate HBI database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    opl.args.add_inventory_db_opts(parser)

    with opl.skelet.test_setup(parser) as (args, status_data):
        cleanup(args, status_data)
