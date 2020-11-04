import logging

import json
import requests
import tempfile

import opl.status_data


def load(server, index, query, paths):
    out = {}

    for path in paths:
        out[path] = []

    url = f"{server}/{index}/_search"
    headers = {
        'Content-Type': 'application/json',
    }
    data = query
    logging.info(f"Querying ES with url={url}, headers={headers} and json={json.dumps(data)}")

    response = requests.get(url, headers=headers, json=data)
    response.raise_for_status()
    logging.debug(f"Got back this: {response.json()}")

    for item in response.json()['hits']['hits']:
        tmpfile = tempfile.NamedTemporaryFile(prefix=item['_id'], delete=False).name
        sd = opl.status_data.StatusData(tmpfile, data=item['_source'])
        for path in paths:
            tmp = sd.get(path)
            if tmp is not None:
                out[path].append(tmp)

    logging.debug(f"Loaded {out}")
    return out
