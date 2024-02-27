#!/usr/bin/env python3

import logging
import time
from kafka import TopicPartition
from opl.kafka_init import kafka_init


class ConsumerLag:
    """
    ConsumerLag gets the lag info for a particular topic of all the partitions by providing
    bootstrap_server and kafka group as input.
    """

    def __init__(self, args, kafka_topic) -> None:
        self.args = args
        self.args.kafka_topic = kafka_topic
        self.logger = logging.getLogger("consumer_lag")
        self.offset_records = {}

    def _getconsumer(self):
        self.args.kafka_max_poll_records = 50
        self.args.kafka_max_poll_interval_ms = 300000
        self.args.kafka_session_timeout_ms = 50000
        self.args.kafka_heartbeat_interval_ms = 10000
        self.args.kafka_timeout = 100000

        return kafka_init.get_consumer(self.args)

    def store_offset_records(self):
        consumer = self._getconsumer()
        partition_set = consumer.partitions_for_topic(self.args.kafka_topic)
        counter = 0
        while counter < 5:
            counter += 1
            partition_set = consumer.partitions_for_topic(self.args.kafka_topic)
            if partition_set:
                break
            else:
                time.sleep(10)

        partitions = []
        for partition_id in partition_set:
            partitions.append(TopicPartition(self.args.kafka_topic, partition_id))

        curr_offsets = {}
        for partition in partitions:
            committed = consumer.committed(partition)
            curr_offsets[partition.partition] = committed

        end_offsets = consumer.end_offsets(partitions)

        for partition_id, value in curr_offsets.items():
            record = {
                "curr_offset": value,
                "end_offset": end_offsets[
                    TopicPartition(topic=self.args.kafka_topic, partition=partition_id)
                ],
            }
            self.offset_records[partition_id] = record

    def get_lag(self):
        self.store_offset_records()
        response = True
        for _, record in self.offset_records.items():
            if record["curr_offset"] is None:
                self.logger.warning(
                    f"For some reason current offset is None, replacing it with 0 in: {record}"
                )
                record["curr_offset"] = 0
            diff = record["end_offset"] - record["curr_offset"]
            if diff == 0:
                response *= True
            else:
                response *= False

        return response
