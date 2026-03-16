#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import socket

import opl.generators.inventory_egress
import opl.post_kafka_times


def func_add_more_args(parser):
    parser.add_argument(
        "--count",
        default=100,
        type=int,
        help="How many messages to prepare",
    )
    parser.add_argument(
        "--n-packages",
        default=500,
        type=int,
        help="How many packages addresses should each host have",
    )
    parser.add_argument(
        "--msg-type",
        default="created",
        choices=["created"],
        help="Type of the message",
    )


def func_return_generator(args):
    return opl.generators.inventory_egress.EgressHostsGenerator(
        count=args.count,
        n_packages=args.n_packages,
        msg_type=args.msg_type,
    )


def func_return_message_payload(args, message_id, message):
    return json.dumps(message)


def func_return_message_key(args, message_id, message):
    return message_id


def func_return_message_headers(args, message_id, message):
    _event_type = args.msg_type
    _request_id = message["platform_metadata"]["request_id"]
    _producer = socket.gethostname()
    _insights_id = message["host"]["insights_id"]
    return [
        ("event_type", _event_type),
        ("request_id", _request_id),
        ("producer", _producer),
        ("insights_id", _insights_id),
    ]


if __name__ == "__main__":
    config = {
        "func_add_more_args": func_add_more_args,
        "query_store_info_produced": "query_store_info_produced",
        "func_return_generator": func_return_generator,
        "func_return_message_payload": func_return_message_payload,
        "func_return_message_headers": func_return_message_headers,
        "func_return_message_key": func_return_message_key,
    }
    opl.post_kafka_times.post_kafka_times(config)
