import json
import logging
import tempfile

import opl.http
import opl.status_data


def load(server, index, query, paths):
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
