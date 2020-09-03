import os
import socket


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
                        help='Kafka timeout (also use env variable KAFKA_TIMEOUT)')
    parser.add_argument('--kafka-group',
                        default=os.getenv('KAFKA_GROUP', f"perf-test-{socket.gethostname()}"),
                        help='Kafka consumer group (also use env variable KAFKA_GROUP)')


def add_locust_opts(parser):
    # Is this a simple local runner or master or slave?
    parser.add_argument('--locust-local-runner', action='store_true',
                        default=True if os.getenv('LOCUST_LOCAL_RUNNER', 'true') == 'true' else False,
                        help='Make this a local runner (also use env variable LOCUST_LOCAL_RUNNER)')
    parser.add_argument('--locust-master-runner', action='store_true',
                        default=True if os.getenv('LOCUST_MASTER_RUNNER', 'false') == 'true' else False,
                        help='Make this a master runner (also use env variable LOCUST_MASTER_RUNNER)')
    parser.add_argument('--locust-slave-runner', action='store_true',
                        default=True if os.getenv('LOCUST_SLAVE_RUNNER', 'false') == 'true' else False,
                        help='Make this a slave runner (also use env variable LOCUST_SLAVE_RUNNER)')

    # Master specific parameters
    parser.add_argument('--locust-master-expect-slaves',
                        dest='expect_slaves', type=int,
                        default=int(os.getenv('LOCUST_MASTER_EXPECT_SLAVES', 1)),
                        help='How many slaves to expect before starting the test (also use env variable LOCUST_MASTER_EXPECT_SLAVES)')

    # Slave specific parameters
    parser.add_argument('--locust-slave-master-host', dest='master_host',
                        default=os.getenv('LOCUST_SLAVE_MASTER_HOST', 'localhost'),
                        help='Master host to connect to (also use env variable LOCUST_SLAVE_MASTER_HOST)')

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
