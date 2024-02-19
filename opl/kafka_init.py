from kafka import KafkaProducer, KafkaConsumer

import logging

# Common instantiators for KafkaProducer and KafkaConsumer


class kafka_init:

    def kafka_bootstrap(args):
        try:
            return args.kafka_bootstrap
        except AttributeError:
            try:
                if args.kafka_hosts != "":
                    return args.kafka_hosts.split(",")
            except AttributeError:
                pass
        return f"{args.kafka_host}:{args.kafka_port}"

    # Based on the args, obtain KafkaProducer instance
    def get_producer(args, status_data=None):
        bootstrap_servers = kafka_bootstrap(args)

        # Sanitize acks setting
        if args.kafka_acks != "all":
            args.kafka_acks = int(args.kafka_acks)

        if hasattr(args, "dry_run") and args.dry_run:
            logging.info("NOT creating a producer as this is a dry run")
            producer = None
        else:
            common_params = {
                "bootstrap_servers": bootstrap_servers,
                "acks": getattr(args, "kafka_acks", None),
                "request_timeout_ms": getattr(args, "kafka_request_timeout_ms", 30000),
                "max_block_ms": getattr(args, "kafka_max_block_ms", 60000),
                "linger_ms": getattr(args, "kafka_linger_ms", 0),
                "compression_type": getattr(args, "kafka_compression_type", None),
                "batch_size": getattr(args, "kafka_batch_size", 16384),
                "buffer_memory": getattr(args, "kafka_buffer_memory", 33554432),
                "retries": getattr(args, "kafka_retries", 0),
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

            if status_data is not None:
                status_data.set("parameters.kafka.bootstrap", bootstrap_servers)
                status_data.set("parameters.kafka.group", args.kafka_group)
                status_data.set("parameters.kafka.topic", args.kafka_topic)
                status_data.set("parameters.kafka.timeout", args.kafka_timeout)

            return producer

    # Based on the args, obtain KafkaConsumer instance.
    # If args.kafka_topic is supplied, subscribe to the topic.
    def get_consumer(args, status_data=None):
        bootstrap_servers = kafka_bootstrap(args)

        # Common parameters for both cases
        common_params = {
            "bootstrap_servers": bootstrap_servers,
            "auto_offset_reset": getattr(args, "kafka_auto_offset_reset", "latest"),
            "enable_auto_commit": getattr(args, "kafka_enable_auto_commit", False),
            "max_poll_records": getattr(args, "kafka_max_poll_records", 50),
            "max_poll_interval_ms": getattr(args, "kafka_max_poll_interval_ms", 300000),
            "group_id": getattr(args, "kafka_group", None),
            "session_timeout_ms": getattr(args, "kafka_session_timeout_ms", 50000),
            "heartbeat_interval_ms": getattr(
                args, "kafka_heartbeat_interval_ms", 10000
            ),
            "consumer_timeout_ms": getattr(args, "kafka_timeout", 100000),
        }

        # Kafka consumer creation: SASL or noauth
        if args.kafka_username != "" and args.kafka_password != "":
            logging.info(
                f"Creating SASL password-protected Kafka consumer for {bootstrap_servers} in group {common_params['group_id']} with timeout {common_params['session_timeout_ms']} ms"
            )
            sasl_params = {
                "security_protocol": "SASL_SSL",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": args.kafka_username,
                "sasl_plain_password": args.kafka_password,
            }
            consumer = KafkaConsumer(**common_params, **sasl_params)
        else:
            logging.info(
                f"Creating passwordless Kafka consumer for {bootstrap_servers} in group {common_params['group_id']} with timeout {common_params['session_timeout_ms']} ms"
            )
            consumer = KafkaConsumer(**common_params)

        if status_data is not None:
            status_data.set("parameters.kafka.bootstrap", bootstrap_servers)
            status_data.set("parameters.kafka.group", args.kafka_group)
            status_data.set("parameters.kafka.topic", args.kafka_topic or "")
            status_data.set("parameters.kafka.timeout", args.kafka_timeout)

        if args.kafka_topic and args.kafka_topic != "":
            consumer.subscribe([args.kafka_topic])

        return consumer
