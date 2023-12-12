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


# collect_info could be None
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

        if collect_info is not None:
            # Add currently processed host to data
            if message["data"]["account"] not in collect_info["accounts"]:
                collect_info["accounts"][message["data"]["account"]] = []
            current_info = {
                "fqdn": message["data"]["fqdn"],
                "subscription_manager_id": message["data"]["subscription_manager_id"],
                "org_id": message["data"]["org_id"],
            }
            if "insights_id" in message["data"]:
                current_info["insights_id"] = message["data"]["insights_id"]
            collect_info["accounts"][message["data"]["account"]].append(current_info)

        value = json.dumps(message).encode()

        if args.dry_run:
            handle_send_success(data_stats=data_stats, data_lock=data_lock)
        else:
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

    if not args.dry_run:
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


def fetch_records_count(inventory):
    inventory_cursor = inventory.cursor()
    inventory_cursor.execute("select count(*) as exact_count from hosts")
    for i in inventory_cursor.fetchone():
        existing_records = int(i)

    return existing_records


def verify(args, previous_records, status_data, inventory, collect_info):
    # Generatate set of IDs to check in the DB
    inventory_cursor = inventory.cursor()

    batch_size = 100  # how many IDs to check in one go
    attempt = 0
    attempts_max = (args.count // batch_size + 1) * 10
    expected_ids = previous_records + args.count  # number of records exist after test
    while True:
        existing_ids = fetch_records_count(inventory)

        # Are we done yet?
        if existing_ids == expected_ids:
            logging.info("All IDs present in the Inventory DB")
            break

        # Are we out of attempts?
        attempt += 1
        if attempt > attempts_max:
            raise Exception(
                f"After {attempt} attempts, we only have {existing_ids} out of {args.count}"
            )

        # If there were no new hosts now, wait a bit
        if existing_ids != expected_ids:
            logging.debug(
                f"Waiting for IDs, attempt {attempt}, remaining {existing_ids}"
            )
            time.sleep(15)

    inventory_cursor.close()


def gen_send_verify(args, status_data):
    logging.info("Creating payload generation instance")
    payload_generator = opl.generators.inventory_ingress.InventoryIngressGenerator(
        count=args.count,
        relatives=args.relatives,
        packages=args.packages,
        template=args.template,
        addresses=args.addresses,
        mac_addresses=args.mac_addresses,
    )

    logging.info("Creating Inventory DB connection")
    inventory_db_conf = {
        "host": args.inventory_db_host,
        "port": args.inventory_db_port,
        "database": args.inventory_db_name,
        "user": args.inventory_db_user,
        "password": args.inventory_db_pass,
    }
    if args.dry_run:
        inventory = None
        exist_records_in_db = 0
    else:
        inventory = psycopg2.connect(**inventory_db_conf)
        exist_records_in_db = fetch_records_count(
            inventory
        )  # fetch existing records count

    kafka_host = f"{args.kafka_host}:{args.kafka_port}"
    logging.info(f"Creating producer to {kafka_host}")
    if args.dry_run:
        producer = None
    else:
        try:
            logging.info(
                f"Creating SASL password-protected producer to {args.kafka_host}"
            )
            producer = kafka.KafkaProducer(
                bootstrap_servers=kafka_host,
                # api_version=(0, 10),
                security_protocol="SASL_SSL",
                sasl_mechanism="SCRAM-SHA-512",
                sasl_plain_username=args.kafka_username,
                sasl_plain_password=args.kafka_password,
            )
        except AttributeError:
            logging.info(f"Creating passwordless producer to {args.kafka_host}")
            producer = kafka.KafkaProducer(
                bootstrap_servers=kafka_host,
                api_version=(0, 10),
            )

        status_data.set("parameters.kafka.bootstrap", kafka_host)

    logging.info("Creating data structure to store list of accounts and so")
    collect_info = {"accounts": {}}  # simplified info about hosts
    if args.no_check:  # don't keep the account info since it's too big
        collect_info = None

    gen_and_send(
        args,
        status_data,
        payload_generator=payload_generator,
        producer=producer,
        collect_info=collect_info,
    )
    if not (args.dry_run or args.no_check):
        verify(
            args,
            exist_records_in_db,
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
        "--addresses",
        default=3,
        type=int,
        help="How many IPv4 and IPv6 adresses to put into the host",
    )
    parser.add_argument(
        "--mac-addresses",
        default=1,
        type=int,
        help="How many MAC adresses to put into the host",
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
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Use this for debugging if you do not want to actuall send the messages",
    )
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Enable sending of hosts without checking if they appear in HBI. Good for Perf testing.",
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
    inventory_cursor.execute("TRUNCATE hosts CASCADE")
    inventory.commit()

    status_data.set_now("parameters.inventory_db.table_hosts.truncated_at")


def cleanup_main():
    parser = argparse.ArgumentParser(
        description="Truncate HBI database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    opl.args.add_inventory_db_opts(parser)

    with opl.skelet.test_setup(parser) as (args, status_data):
        cleanup(args, status_data)
