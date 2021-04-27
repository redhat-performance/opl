import os
import socket
import argparse


def _add_generic_db_opts(parser, name):
    name_lower = name.lower()
    name_upper = name.upper()
    name_camel = f"{name_upper[0]}{name_lower[1:]}"
    parser.add_argument(f'--{name_lower}-db-host',
                        default=os.getenv(f'{name_upper}_DB_HOST', 'localhost'),
                        help=f'{name_camel} DB host (also use env variable {name_upper}_DB_HOST)')
    parser.add_argument(f'--{name_lower}-db-port',
                        default=os.getenv(f'{name_upper}_DB_PORT', '5432'),
                        help=f'{name_camel} DB port (also use env variable {name_upper}_DB_PORT)')
    parser.add_argument(f'--{name_lower}-db-name',
                        default=os.getenv(f'{name_upper}_DB_NAME', name_lower),
                        help=f'{name_camel} DB database name (also use env variable {name_upper}_DB_NAME)')
    parser.add_argument(f'--{name_lower}-db-user',
                        default=os.getenv(f'{name_upper}_DB_USER', name_lower),
                        help=f'{name_camel} DB username (also use env variable {name_upper}_DB_USER)')
    parser.add_argument(f'--{name_lower}-db-pass',
                        default=os.getenv(f'{name_upper}_DB_PASS', name_lower),
                        help=f'{name_camel} DB password (also use env variable {name_upper}_DB_PASS)')


def add_cyndi_db_opts(parser):
    _add_generic_db_opts(parser, 'cyndi')


def add_storage_db_opts(parser):
    _add_generic_db_opts(parser, 'storage')


def add_subscriptions_db_opts(parser):
    _add_generic_db_opts(parser, 'subscriptions')


def add_inventory_db_opts(parser):
    _add_generic_db_opts(parser, 'inventory')


def add_patchman_db_opts(parser):
    _add_generic_db_opts(parser, 'patchman')


def add_rbac_db_opts(parser):
    _add_generic_db_opts(parser, 'rbac')


def add_remediations_db_opts(parser):
    _add_generic_db_opts(parser, 'remediations')


def add_vulnerability_db_opts(parser):
    _add_generic_db_opts(parser, 'vulnerability')


def add_kafka_opts(parser):
    parser.add_argument('--kafka-host',
                        default=os.getenv('KAFKA_HOST', 'localhost'),
                        help='Kafka host (also use env variable KAFKA_HOST)')
    parser.add_argument('--kafka-port', type=int,
                        default=int(os.getenv('KAFKA_PORT', 9092)),
                        help='Kafka port (also use env variable KAFKA_PORT)')
    parser.add_argument('--kafka-timeout', type=int,
                        default=int(os.getenv('KAFKA_TIMEOUT', 100000)),
                        help='Kafka timeout when consuming messages (also use env variable KAFKA_TIMEOUT)')
    parser.add_argument('--kafka-group',
                        default=os.getenv('KAFKA_GROUP', f"perf-test-{socket.gethostname()}"),
                        help='Kafka consumer group (also use env variable KAFKA_GROUP)')


def add_mosquitto_opts(parser):
    parser.add_argument('--mosquitto-host',
                        default=os.getenv('MOSQUITTO_HOST', 'localhost'),
                        help='Mosquitto host (also use env variable MOSQUITTO_HOST)')
    parser.add_argument('--mosquitto-port', type=int,
                        default=int(os.getenv('MOSQUITTO_PORT', 8883)),
                        help='Mosquitto port (also use env variable MOSQUITTO_PORT)')
    parser.add_argument('--mosquitto-timeout', type=int,
                        default=int(os.getenv('MOSQUITTO_TIMEOUT', 60)),
                        help='Mosquitto timeout (also use env variable MOSQUITTO_TIMEOUT)')
    parser.add_argument('--mosquitto-username',
                        default=os.getenv('MOSQUITTO_USERNAME', None),
                        help='Mosquitto username (also use env variable MOSQUITTO_USERNAME)')
    parser.add_argument('--mosquitto-password',
                        default=os.getenv('MOSQUITTO_PASSWORD', None),
                        help='Mosquitto password (also use env variable MOSQUITTO_PASSWORD)')
    parser.add_argument('--mosquitto-tls', action='store_true', default=False,
                        help='Setup TLS when talking to mosquitto host')
    parser.add_argument('--mosquitto-transport',
                        default=os.getenv('MOSQUITTO_TRANSPORT', 'tcp'),
                        choices=['tcp', 'websockets'],
                        help='Mosquitto transport (also use env variable MOSQUITTO_TRANSPORT)')
    parser.add_argument('--mosquitto-topic-prefix',
                        default=os.getenv('MOSQUITTO_TOPIC_PREFIX', 'perf'),
                        help='Mosquitto topic prefix (also use env variable MOSQUITTO_TOPIC_PREFIX)')


def add_s3_opts(parser):
    parser.add_argument('--s3-aws-access-key-id',
                        default=os.getenv('S3_AWS_ACCESS_KEY_ID', 'abcdef'),
                        help='AWS S3 access key ID (also use env variable S3_AWS_ACCESS_KEY_ID)')
    parser.add_argument('--s3-aws-region',
                        default=os.getenv('S3_AWS_REGION', 'us-east-1'),
                        help='AWS S3 region (also use env variable S3_AWS_REGION)')
    parser.add_argument('--s3-aws-secret-access-key',
                        default=os.getenv('S3_AWS_SECRET_ACCESS_KEY', 'abcdef'),
                        help='AWS S3 secret access key (also use env variable S3_AWS_SECRET_ACCESS_KEY)')
    parser.add_argument('--s3-bucket',
                        default=os.getenv('S3_BUCKET', 'abcdef'),
                        help='AWS S3 bucket (also use env variable S3_BUCKET)')
    parser.add_argument('--s3-endpoint',
                        default=os.getenv('S3_ENDPOINT', 'abcdef'),
                        help='AWS S3 endpoint (also use env variable S3_ENDPOINT)')


def add_locust_opts(parser):
    # Is this a simple local runner or master or worker?
    parser.add_argument('--locust-local-runner', action='store_true',
                        default=True if os.getenv('LOCUST_LOCAL_RUNNER', 'true') == 'true' else False,
                        help='Make this a local runner (also use env variable LOCUST_LOCAL_RUNNER)')
    parser.add_argument('--locust-master-runner', action='store_true',
                        default=True if os.getenv('LOCUST_MASTER_RUNNER', 'false') == 'true' else False,
                        help='Make this a master runner which does not do any requests (also use env variable LOCUST_MASTER_RUNNER)')
    parser.add_argument('--locust-worker-runner', action='store_true',
                        default=True if os.getenv('LOCUST_WORKER_RUNNER', 'false') == 'true' else False,
                        help='Make this a worker runner (also use env variable LOCUST_WORKER_RUNNER)')

    # Master specific parameters
    parser.add_argument('--locust-master-expect-workers',
                        dest='expect_workers', type=int,
                        default=int(os.getenv('LOCUST_MASTER_EXPECT_WORKERS', 1)),
                        help='How many workers to expect before starting the test (also use env variable LOCUST_MASTER_EXPECT_WORKERS)')

    # Worker specific parameters
    parser.add_argument('--locust-worker-master-host', dest='master_host',
                        default=os.getenv('LOCUST_WORKER_MASTER_HOST', 'localhost'),
                        help='Master host to connect to port 5557 (also use env variable LOCUST_WORKER_MASTER_HOST)')

    # Locust run parameters
    parser.add_argument('--locust-num-clients', dest='num_clients', type=int,
                        default=int(os.getenv('LOCUST_NUM_CLIENTS', 100)),
                        help='Locust number of clients (also use env variable LOCUST_NUM_CLIENTS)')
    parser.add_argument('--locust-hatch-rate', dest='hatch_rate', type=int,
                        default=int(os.getenv('LOCUST_HATCH_RATE', 10)),
                        help='Locust hatch rate (also use env variable LOCUST_HATCH_RATE)')
    parser.add_argument('--locust-host', dest='host',
                        default=os.getenv('LOCUST_HOST', 'http://rbac.qa.svc:8080'),
                        help='Locust host to test (also use env variable LOCUST_HOST)')
    parser.add_argument('--locust-stop-timeout', dest='stop_timeout', type=int,
                        default=int(os.getenv('LOCUST_STOP_TIMEOUT', 10)),
                        help='Locust stop timeout (also use env variable LOCUST_STOP_TIMEOUT)')

    # Our test specific parameters
    parser.add_argument('--test-duration', type=int,
                        default=os.getenv('TEST_DURATION', 100),
                        help='Test duration (also use env variable TEST_DURATION)')
    parser.add_argument('--test-requests', type=int,
                        default=os.getenv('TEST_REQUESTS', 0),
                        help='Number of requests - if non-0, this overrides test duration (also use env variable TEST_REQUESTS)')
    parser.add_argument('--test-url-suffix',
                        default=os.getenv('TEST_URL_SUFFIX', '/api/rbac/v1'),
                        help='Test host URL suffix (also use env variable TEST_URL_SUFFIX)')


def add_tables_def_opts(parser):
    parser.add_argument('--tables-definition', type=argparse.FileType('r'),
                        default=open(os.getenv('TABLES_DEFINITION', 'tables.yaml'), 'r'),
                        help='File defining tables and SQL to create them (also use env variable TABLES_DEFINITION)')
