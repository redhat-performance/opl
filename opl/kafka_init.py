import kafka

# from . import status_data
import logging

### Common instantiators for KafkaProducer and KafkaConsumer


def kafka_bootstrap(args):
    if args.kafka_bootstrap:
        return args.kafka_bootstrap
    if args.kafka_hosts != None and args.kafka_hosts != "":
        return args.kafka_hosts.split(",")
    else:
        return f"{args.kafka_host}:{args.kafka_port}"


# From args, obtain
def get_producer(args, status_data=None):
    bootstrap_servers = kafka_bootstrap(args)

    # Sanitize acks setting
    if args.kafka_acks != "all":
        args.kafka_acks = int(args.kafka_acks)

    if args.dry_run:
        logging.info(f"NOT creating a producer as this is a dry run")
        producer = None
    else:
        common_params = {
            "bootstrap_servers": bootstrap_servers,
            "acks": args.kafka_acks,
            "request_timeout_ms": args.kafka_request_timeout_ms or 30000,
            "max_block_ms": args.kafka_max_block_ms or 60000,
            "linger_ms": args.kafka_linger_ms or 0,
            "compression_type": args.kafka_compression_type or None,
            "batch_size": args.kafka_batch_size or 16384,
            "buffer_memory": args.kafka_buffer_memory or 33554432,
            "retries": args.kafka_retries or 0,
        }

        if args.kafka_username != "" and args.kafka_password != "":
            logging.info(
                f"Creating SASL password-protected producer to {bootstrap_servers}"
            )
            sasl_params = {
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": args.kafka_username,
                "sasl_plain_password": args.kafka_password,
            }
            producer = KafkaProducer(**common_params, **sasl_params)
        else:
            logging.info(f"Creating passwordless producer to {bootstrap_servers}")
            producer = KafkaProducer(**common_params)

        if status_data != None:
            status_data.set("parameters.kafka.bootstrap", bootstrap_servers)
            status_data.set("parameters.kafka.group", args.kafka_group)
            status_data.set("parameters.kafka.topic", args.kafka_topic)
            status_data.set("parameters.kafka.timeout", args.kafka_timeout)

        return producer


def get_consumer(args, status_data=None):
    bootstrap_servers = kafka_bootstrap(args)

    # Common parameters for both cases
    common_params = {
        "bootstrap_servers": args.bootstrap_servers,
        "auto_offset_reset": args.auto_offset_reset or "latest",
        "enable_auto_commit": args.enable_auto_commit or False,
        "max_poll_records": args.max_poll_records or 50,
        "max_poll_interval_ms": args.max_poll_interval_ms or 300000,
        "group_id": args.kafka_group,
        "session_timeout_ms": args.session_timeout_ms or 50000,
        "heartbeat_interval_ms": args.heartbeat_interval_ms or 10000,
        "consumer_timeout_ms": args.kafka_timeout or 100000,
    }

    # Kafka consumer creation: SASL or noauth
    if args.username != "" and args.password != "":
        logging.info(
            f"Creating SASL password-protected Kafka consumer for {args.bootstrap_servers} in group {args.kafka_group} with timeout {args.session_timeout_ms or 50000} ms"
        )
        sasl_params = {
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "SCRAM-SHA-512",
            "sasl_plain_username": args.username,
            "sasl_plain_password": args.password,
        }
        consumer = KafkaConsumer(**common_params, **sasl_params)
    else:
        logging.info(
            f"Creating passwordless Kafka consumer for {args.bootstrap_servers} in group {args.kafka_group} with timeout {common_params['session_timeout_ms']} ms"
        )
        consumer = KafkaConsumer(**common_params)

    if status_data != None:
        status_data.set("parameters.kafka.bootstrap", bootstrap_servers)
        status_data.set("parameters.kafka.group", args.kafka_group)
        status_data.set("parameters.kafka.topic", args.kafka_topic or "")
        status_data.set("parameters.kafka.timeout", args.kafka_timeout)

    if args.kafka_topic and args.kafka_topic != "":
        consumer.subscribe([args.kafka_topic])

    return consumer
