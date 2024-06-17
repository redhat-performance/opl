import logging
import os
import time
from contextlib import contextmanager
from functools import wraps

from . import status_data


@contextmanager
def test_setup(parser):
    parser.add_argument(
        "--status-data-file",
        default=os.getenv("STATUS_DATA_FILE", "/tmp/status-data.json"),
        help='File where we maintain metadata, results, parameters and measurements for this test run (also use env variable STATUS_DATA_FILE, default to "/tmp/status-data.json")',
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Be verbose - show info output"
    )
    args = parser.parse_args()

    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
    if args.debug:
        logging.basicConfig(format=fmt, level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(format=fmt, level=logging.INFO)
    else:
        logging.basicConfig(format=fmt)

    logging.debug(f"Args: {args}")

    sdata = status_data.StatusData(args.status_data_file)

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
                    logging.debug(f"Retrying in {wait_seconds} seconds. Attempt {attempt}/{max_attempts} failed with: {e}")
                    time.sleep(wait_seconds)

        return wrapper
    return decorator
