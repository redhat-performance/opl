import time
import logging
from functools import wraps


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
