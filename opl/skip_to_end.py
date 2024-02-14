#!/usr/bin/env python3

import logging
import argparse
import os
import time

from . import kafka_init
from . import args
from . import skelet


def doit_seek_to_end(args):
    """
    Create consumer and seek to end

    This seek to end is important so we are not wasting our time processing
    all the messages in the Kafka log for given topic. If we would have same
    and static group name, we would have problems when running concurrently
    on multiple pods.
    """

    args.enable_auto_commit = True
    consumer = kafka_init.get_consumer(args)

    # Seek to end
    for attempt in range(10):
        try:
            consumer.poll(timeout_ms=0)
            consumer.seek_to_end()
        except AssertionError as e:
            logging.warning(f"Retrying as seek to end failed with: {e}")
            time.sleep(1)
        else:
            break
    else:
        logging.error("Out of attempts when trying to seek to end")

    for _ in consumer:
        print(".", end="")
    consumer.close()


def doit(args, status_data):
    doit_seek_to_end(args, status_data)

    status_data.set("parameters.kafka.seek_topic", args.kafka_topic)
    status_data.set("parameters.kafka.seek_timeout", args.kafka_timeout)
    status_data.set_now("parameters.kafka.seek_at")


def main():
    parser = argparse.ArgumentParser(
        description="Skip to end of the given Kafka topic",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--kafka-topic",
        default=os.getenv("KAFKA_TOPIC", "platform.receptor-controller.responses"),
        help="Topic for which to skip to end (also use env variable KAFKA_TOPIC)",
    )
    args.add_kafka_opts(parser)

    with skelet.test_setup(parser) as (params, status_data):
        doit(params, status_data)
