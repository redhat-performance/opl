import logging

import requests
from requests.auth import HTTPBasicAuth
import urllib3
import os

enable_new_search = os.getenv('NEW_SEARCH_ENABLED', 'false').lower() == 'true'

if enable_new_search:
    username = os.getenv('OPEN_SEARCH_DASBOARD')
    password = os.getenv('OPEN_SEARCH_PASSWORD')
    session = requests.Session()
    session.auth = HTTPBasicAuth(username, password)
    session.verify = False
    session.headers.update({
        "Content-Type": "application/json",
    })
else:
    session = requests.Session()

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
