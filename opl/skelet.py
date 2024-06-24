import logging
import logging.handlers
import os
import time
from contextlib import contextmanager
from functools import wraps
from . import status_data

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

    sdata = status_data.create_status_data(args.status_data_file)

    try:
        yield (args, sdata)
    finally:
        sdata.save()


def retry_on_traceback(max_attempts=10, wait_seconds=1):
    """
    Retries a function until it succeeds or the maximum number of attempts
    or wait time is reached.

    This is to mimic `@retry` decorator from Tenacity so we do not depend
    on it.

    Args:
        max_attempts: The maximum number of attempts to retry the function.
        wait_seconds: The number of seconds to wait between retries.

    Returns:
        A decorator that retries the wrapped function.
    """
    assert max_attempts >= 0, "It does not make sense to have less than 0 retries"
    assert wait_seconds >= 0, "It does not make sense to wait les than 0 seconds"

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= max_attempts:
                        raise  # Reraise the exception after all retries are exhausted

                    attempt += 1
                    logging.debug(
                        f"Retrying in {wait_seconds} seconds. Attempt {attempt}/{max_attempts} failed with: {e}"
                    )
                    time.sleep(wait_seconds)

        return wrapper

    return decorator