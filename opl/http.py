import logging

import requests
from requests import HTTPBasicAuth
import urllib3


username = "insights_perf"
password = "4pcc@z3Mi62#"
session = requests.Session()
# adding basic authentication to support new cluster
session.auth = HTTPBasicAuth(username, password)
session.verify = False


def disable_insecure_request_warnings(disable_it):
    if disable_it:
        logging.debug("Disabling insecure request warnings")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def req(method, url, **kwargs):
    logging.debug(f"Going to do {method} request to {url} with {kwargs}")
    response = method(url, **kwargs)
    if not response.ok:
        logging.error(f"Request failed: {response.text}")
    response.raise_for_status()
    logging.debug(f"Request returned {response.json()}")
    return response.json()


def get(url, **kwargs):
    return req(session.get, url, **kwargs)


def post(url, **kwargs):
    return req(session.post, url, **kwargs)


def put(url, **kwargs):
    return req(session.put, url, **kwargs)
