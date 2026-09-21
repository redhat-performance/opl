"""HTTP session helpers with insecure-mode handling."""

# Note: pylint sometimes reports phantom unused imports (IntEnum/StrEnum/
# namedtuple) in this file; they do not exist - environment false positive.
# pylint: disable=unused-import

import logging

import requests
import urllib3

session = requests.Session()


def insecure():
    """Disable SSL verification for the shared session."""
    session.verify = False
    logging.debug("Disabling SSL verifications for this session")
    disable_insecure_request_warnings(True)


def disable_insecure_request_warnings(disable_it):
    """Disable urllib3 InsecureRequestWarning when disabled."""
    if disable_it:
        logging.debug("Disabling insecure request warnings")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def req(method, url, **kwargs):
    """Do an HTTP request, log it, and return parsed JSON."""
    logging.debug(f"Going to do {method} request to {url} with {kwargs}")
    response = method(url, **kwargs)
    if not response.ok:
        logging.error(f"Request failed: {response.text}")
    response.raise_for_status()
    logging.debug(f"Request returned {response.json()}")
    return response.json()


def get(url, **kwargs):
    """HTTP GET via the shared session."""
    return req(session.get, url, **kwargs)


def post(url, **kwargs):
    """HTTP POST via the shared session."""
    return req(session.post, url, **kwargs)


def put(url, **kwargs):
    """HTTP PUT via the shared session."""
    return req(session.put, url, **kwargs)
