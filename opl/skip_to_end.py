#!/usr/bin/env python3

import logging
import argparse
import os
import time

from kafka import KafkaConsumer

from . import args
from . import skelet


def doit_seek_to_end(kafka_hosts, kafka_timeout, kafka_topic, kafka_group, args=""):
    """
    Create consumer and seek to end

    This seek to end is important so we are not wasting our time processing
    all the messages in the Kafka log for given topic. If we would have same
    and static group name, we would have problems when running concurrently
    on multiple pods.
    """

    # Common parameters for both cases
    common_params = {
        bootstrap_servers: kafka_hosts,
        auto_offset_reset: "latest",
        enable_auto_commit: True,
        group_id: kafka_group,
        session_timeout_ms: 50000,
        heartbeat_interval_ms: 10000,
        consumer_timeout_ms: kafka_timeout,
    }

    # Kafka consumer creation: SASL or noauth
    try:
        logging.info(
            f"Creating SASL password-protected Kafka consumer for {kafka_hosts} in group {kafka_group} with timeout {kafka_timeout} ms topic {kafka_topic}"
        )
        sasl_params = {
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "SCRAM-SHA-512",
            "sasl_plain_username": args.kafka_username,
            "sasl_plain_password": args.kafka_password,
        }
        consumer = KafkaConsumer(**common_params, **sasl_params)
    except AttributeError:
        logging.info(
            f"Creating passwordless producer for for {kafka_hosts} in group {kafka_group} with timeout {kafka_timeout} ms topic {kafka_topic}"
        )
        consumer = KafkaConsumer(**common_params)

    consumer.subscribe(kafka_topic)

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
    doit_seek_to_end(
        [f"{args.kafka_host}:{args.kafka_port}"],
        args.kafka_timeout,
        args.kafka_topic,
        args.kafka_group,
        args,
    )

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
