import logging

import requests

import urllib3


session = requests.Session()


def disable_insecure_request_warnings(disable_it):
    if disable_it:
        logging.debug("Disabling insecure request warnings")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def req(method, url, headers=None, params=None, data=None, verify=True):
    logging.debug(f"Going to do {method} request to {url} with headers {headers}, params {params} and data {data}")
    response = method(url, params=params, json=data, headers=headers, verify=verify)
    if not response.ok:
        logging.error(f"Request failed: {response.text}")
    response.raise_for_status()
    logging.debug(f"Request returned {response.json()}")
    return response.json()


def get(url, headers=None, params=None, verify=True):
    return req(session.get, url, headers=headers, params=params, verify=verify)


def post(url, headers=None, data=None, verify=True):
    return req(session.post, url, headers=headers, data=data, verify=verify)


def put(url, headers=None, data=None, verify=True):
    return req(session.put, url, headers=headers, data=data, verify=verify)
