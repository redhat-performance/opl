#!/usr/bin/env python3

import logging
import argparse
import socket

from kafka import KafkaConsumer

import opl.args
import opl.skelet


KAFKA_GROUP = f"perf-test-{socket.gethostname()}"


def doit_seek_to_end(kafka_hosts, kafka_timeout, kafka_topic):
    """
    Create consumer and seek to end

    This seek to end is important so we are not wasting our time processing
    all the messages in the Kafka log for given topic. If we would have same
    and static group name, we would have problems when running concurrently
    on multiple pods.
    """
    logging.info(f"Creating Kafka consumer for {kafka_hosts} in group {KAFKA_GROUP} with timeout {kafka_timeout} ms topic {kafka_topic}")
    consumer = KafkaConsumer(
        kafka_topic,
        bootstrap_servers=kafka_hosts,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=KAFKA_GROUP,
        session_timeout_ms=50000,
        heartbeat_interval_ms=10000,
        consumer_timeout_ms=kafka_timeout)
    consumer.poll()
    consumer.seek_to_end()
    for _ in consumer:
        print('.', end='')
    consumer.close()


def doit(args, status_data):
    doit_seek_to_end(
        [f"{args.kafka_host}:{args.kafka_port}"],
        args.kafka_timeout,
        args.kafka_topic)

    status_data.set('parameters.kafka.seek_topic', args.kafka_topic)
    status_data.set('parameters.kafka.seek_timeout', args.kafka_timeout)
    status_data.set_now('parameters.kafka.seek_at')


def main():
    parser = argparse.ArgumentParser(
        description='Skip to end of the given Kafka topic',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--kafka-topic',
                        help='Topic for which to skip to end')
    opl.args.add_kafka_opts(parser)

    with opl.skelet.test_setup(parser) as (args, status_data):
        doit(args, status_data)
