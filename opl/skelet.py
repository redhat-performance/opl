import logging
import logging.handlers
import os
import time
from contextlib import contextmanager
from opl.status import StatusData


def setup_logger(app_name, stderr_log_lvl):
    """
    Create logger that logs to both stderr and log file but with different log levels
    """
    # Remove all handlers from root logger if any
    logging.basicConfig(
        level=logging.NOTSET, handlers=[]
    )  # `force=True` was added in Python 3.8 :-(
    # Change root logger level from WARNING (default) to NOTSET in order for all messages to be delegated
    logging.getLogger().setLevel(logging.NOTSET)

    # Log message format
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(threadName)s %(levelname)s %(message)s"
    )
    formatter.converter = time.gmtime

    # Silence loggers of some chatty libraries we use
    urllib_logger = logging.getLogger("urllib3.connectionpool")
    urllib_logger.setLevel(logging.WARNING)
    selenium_logger = logging.getLogger("selenium.webdriver.remote.remote_connection")
    selenium_logger.setLevel(logging.WARNING)
    kafka_logger = logging.getLogger("kafka")
    kafka_logger.setLevel(logging.WARNING)

    # Add stderr handler, with provided level
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(stderr_log_lvl)
    logging.getLogger().addHandler(console_handler)

    # Add file rotating handler, with level DEBUG
    rotating_handler = logging.handlers.RotatingFileHandler(
        filename=f"/tmp/{app_name}.log", maxBytes=100 * 1000, backupCount=2
    )
    rotating_handler.setFormatter(formatter)
    rotating_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(rotating_handler)

    return logging.getLogger(app_name)


@contextmanager
def test_setup(parser, logger_name="root"):
    parser.add_argument(
        "--status-data-file",
        default=os.getenv("STATUS_DATA_FILE", "/tmp/status-data.json"),
        help='File where we maintain metadata, results, parameters and measurements for this test run (also use env variable STATUS_DATA_FILE, default to "/tmp/status-data.json")',
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Show debug output",
    )
    args = parser.parse_args()

    if args.debug:
        logger = setup_logger(logger_name, logging.DEBUG)
    elif args.verbose:
        logger = setup_logger(logger_name, logging.INFO)
    else:
        logger = setup_logger(logger_name, logging.WARNING)

    logger.debug(f"Args: {args}")

    sdata = StatusData(args.status_data_file)

    try:
        yield (args, sdata)
    finally:
        sdata.save()
