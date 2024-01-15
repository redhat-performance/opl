import json
import logging
import tempfile

import os
import opl.http
import opl.status_data
from requests.auth import HTTPBasicAuth


def load(server, index, query, paths, **kwargs):
    es_server_user = kwargs.get("es_server_user")
    es_server_pass_env_var = kwargs.get("es_server_pass_env_var")

    out = {}

    for path in paths:
        out[path] = []

    url = f"{server}/{index}/_search"
    headers = {
        "Content-Type": "application/json",
    }
    data = query
    logging.info(
        f"Querying ES with url={url}, headers={headers} and json={json.dumps(data)}"
    )

    if es_server_user and es_server_pass_env_var:
        # fetch the password from Jenkins credentials
        open_search_password = os.environ.get(es_server_pass_env_var)
        response = opl.http.get(
            url,
            auth=HTTPBasicAuth(es_server_user, open_search_password),
            headers=headers,
            json=data,
        )
    else:
        response = opl.http.get(url, headers=headers, json=data)

    for item in response["hits"]["hits"]:
        logging.debug(
            f"Loading data from document ID {item['_id']} with field id={item['_source']['id'] if 'id' in item['_source'] else None} or parameters.run={item['_source']['parameters']['run'] if 'run' in item['_source']['parameters'] else None}"
        )
        tmpfile = tempfile.NamedTemporaryFile(prefix=item["_id"], delete=False).name
        sd = opl.status_data.StatusData(tmpfile, data=item["_source"])
        for path in paths:
            tmp = sd.get(path)
            if tmp is not None:
                out[path].append(tmp)

    logging.debug(f"Loaded {out}")
    return out
