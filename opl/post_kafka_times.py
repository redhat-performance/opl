import argparse
import datetime
import logging
import os
import threading
import time

from kafka import KafkaProducer

import opl.args
import opl.data
import opl.db
import opl.skelet

import psycopg2
import psycopg2.extras

import yaml


class PostKafkaTimes:
    def __init__(self, args, status_data, config):
        self.status_data = status_data

        # Sanitize and include args into status data file
        args_copy = vars(args).copy()
        args_copy["tables_definition"] = args_copy["tables_definition"].name
        self.status_data.set("parameters.produce_messages", args_copy)

        storage_db_conf = {
            "host": args.storage_db_host,
            "port": args.storage_db_port,
            "database": args.storage_db_name,
            "user": args.storage_db_user,
            "password": args.storage_db_pass,
        }
        self.connection = psycopg2.connect(**storage_db_conf)
        self.kafka_hosts = [f"{args.kafka_host}:{args.kafka_port}"]
        self.kafka_group = args.kafka_group
        self.kafka_topic = args.kafka_topic
        self.kafka_timeout = args.kafka_timeout
        self.kafka_max_poll_records = 100
        self.queries_definition = yaml.load(
            args.tables_definition, Loader=yaml.SafeLoader
        )["queries"]
        self.show_processed_messages = args.show_processed_messages
        self.rate = args.rate

        self.config = config

        sql = self.queries_definition[self.config["query_store_info_produced"]]
        logging.info(f"Creating storage DB batch inserter with {sql}")
        data_lock = threading.Lock()
        self.save_here = opl.db.BatchProcessor(
            self.connection, sql, batch=100, lock=data_lock
        )

        logging.info("Creating generator")
        self.generator = self.config["func_return_generator"](args)

        logging.info(f"Creating producer to {args.kafka_host}:{args.kafka_port}")
        self.produce_here = KafkaProducer(
            bootstrap_servers=[args.kafka_host + ":" + str(args.kafka_port)],
        )

    def dt_now(self):
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    def work(self):
        def handle_send_success(*args, **kwargs):
            self.save_here.add((kwargs["message_id"], self.dt_now))

        def wait_for_next_second(second=int(time.perf_counter())):
            while second == int(time.perf_counter()):
                time.sleep(0.01)
            return int(time.perf_counter())

        logging.info("Started message generation")
        self.status_data.set_now("parameters.produce.started_at")

        in_second = 0  # how many messages we have sent in this second
        this_second = wait_for_next_second()  # second relevant for in_second

        for message_id, message in self.generator:
            future = self.produce_here.send(self.kafka_topic, value=message)
            future.add_callback(handle_send_success, message_id=message_id)

            if int(time.perf_counter()) == this_second:
                in_second += 1
                if in_second == self.rate:
                    logging.debug(f"In second {this_second} sent {in_second} messages")
                    this_second = wait_for_next_second(this_second)
                    in_second = 0
            else:
                if self.rate != 0 and self.rate != in_second:
                    logging.warning(
                        f"In second {this_second} sent {in_second} messages (but wanted to send {self.rate})"
                    )
                    this_second = int(time.perf_counter())
                    in_second = 0

        self.status_data.set_now("parameters.produce.ended_at")
        logging.info("Finished message generation, producing and storing")

        self.produce_here.flush()

        self.save_here.commit()


def post_kafka_times(config):
    parser = argparse.ArgumentParser(
        description="Given a Kafka messages generator produce messages and put timestamps into DB",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--kafka-topic",
        default=os.getenv("KAFKA_TOPIC", "platform.upload.qpc"),
        help="Produce to this topic (also use env variable KAFKA_TOPIC)",
    )
    parser.add_argument(
        "--show-processed-messages",
        action="store_true",
        help="Show messages we are producing",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=0,
        help="How many messages per second should we produce (0 for no limit)",
    )
    opl.args.add_storage_db_opts(parser)
    opl.args.add_kafka_opts(parser)
    opl.args.add_tables_def_opts(parser)

    # PostKafkaTimes needs this config keys in config dict
    assert "query_store_info_produced" in config
    assert "func_return_generator" in config
    assert "func_add_more_args" in config

    # Add more args
    config["func_add_more_args"](parser)

    with opl.skelet.test_setup(parser) as (args, status_data):
        post_kafka_times_object = PostKafkaTimes(
            args,
            status_data,
            config,
        )
        post_kafka_times_object.work()
