#!/usr/bin/env python3
"""Seek Kafka consumer to the end of the topic."""

import argparse
import logging
import os
import time

from opl import args, skelet
from opl.kafka_init import KafkaInit


def doit_seek_to_end(args):  # pylint: disable=redefined-outer-name
    """
    Seek the consumer to the latest offsets, retrying on races.

    Create consumer and seek to end

    This seek to end is important so we are not wasting our time processing
    all the messages in the Kafka log for given topic. If we would have same
    and static group name, we would have problems when running concurrently
    on multiple pods.
    """

    args.kafka_enable_auto_commit = True
    consumer = KafkaInit.get_consumer(args)

    # Seek to end
    # Partition assignment happens asynchronously during poll(), so a single
    # poll() isn't guaranteed to have completed the consumer group rebalance
    # before we call seek_to_end(). Older kafka-python raises AssertionError
    # for this, newer versions raise ValueError — catch both so the retry
    # loop actually retries instead of crashing on the first race.
    for _attempt in range(10):
        try:
            consumer.poll(timeout_ms=5000)
            consumer.seek_to_end()
        except (AssertionError, ValueError) as e:
            logging.warning('Retrying as seek to end failed with: %s', e)
            time.sleep(1)
        else:
            break
    else:
        logging.error("Out of attempts when trying to seek to end")

    for _ in consumer:
        print(".", end="")
    consumer.close()


def doit(args, status_data):  # pylint: disable=redefined-outer-name
    """Seek consumer to end and store the offsets."""
    doit_seek_to_end(args)

    status_data.set("parameters.kafka.seek_topic", args.kafka_topic)
    status_data.set("parameters.kafka.seek_timeout", args.kafka_timeout)
    status_data.set_now("parameters.kafka.seek_at")


def main():
    """CLI entry point for the skip_to_end tool."""
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
