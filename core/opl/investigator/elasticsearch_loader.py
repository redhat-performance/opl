"""Load data from ElasticSearch for investigation."""

import json
import logging
import os
import tempfile

from requests.auth import HTTPBasicAuth

import opl.http
import opl.status_data


def load(server, index, query, paths, **kwargs):
    """Run query against ElasticSearch and extract given paths."""
    es_server_user = kwargs.get("es_server_user")
    es_server_pass_env_var = kwargs.get("es_server_pass_env_var")
    skip_metadata_assert = kwargs.get("skip_metadata_assert", False)

    out = {}

    for path in paths:
        out[path] = []

    url = f"{server}/{index}/_search"
    headers = {
        "Content-Type": "application/json",
    }
    data = query
    logging.info('Querying ES with url=%s, headers=%s and json=%s', url, headers, json.dumps(data))

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
        params = item["_source"].get("parameters", {})
        logging.debug('Loading data from document ID %s with field id=%s or parameters.run=%s', item['_id'], item['_source'].get('id'), params.get('run'))
        tmpfile = tempfile.NamedTemporaryFile(prefix=item["_id"], delete=False).name  # pylint: disable=consider-using-with  # file must outlive this scope
        sd = opl.status_data.StatusData(
            tmpfile, data=item["_source"], skip_metadata_assert=skip_metadata_assert
        )
        for path in paths:
            tmp = sd.get(path)
            if tmp is not None:
                out[path].append(tmp)

    logging.debug('Loaded %s', out)
    return out
