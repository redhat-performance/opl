import datetime
import json
import logging
import os

import requests


def store(server, index, decisions):

    # This is our workaround on how to add additional metadata about the decision
    job_name = os.environ.get('JOB_NAME', '')
    build_url = os.environ.get('BUILD_URL', '')

    url = f"{server}/{index}/_doc"
    headers = {
        'Content-Type': 'application/json',
    }
    for decision in decisions:
        decision['job_name'] = job_name
        decision['build_url'] = build_url
        decision['uploaded'] = datetime.datetime.utcnow().isoformat()

        ### for k, v in decision.items():
        ###    print(f">>> {k} = {v} ({type(v)})")
        logging.info(f"Storing decision to ES url={url}, headers={headers} and json={json.dumps(decision)}")

        response = requests.post(url, headers=headers, json=decision)

        if not response.ok:
            logging.warning(f"Failed to store decision to ES: {response.text}")
