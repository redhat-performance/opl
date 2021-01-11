import json
import logging
import tempfile

import jinja2

import opl.status_data

import requests

import yaml


def render_query(query, template_data):
    logging.debug(f"Rendering Jinja2 template query {query} with data {template_data}")
    env = jinja2.Environment(
        loader=jinja2.DictLoader({'query': query}))
    template = env.get_template('query')
    rendered = template.render(template_data)
    logging.debug(f"Rendered Jinja2 template query {rendered}")
    return yaml.load(rendered, Loader=yaml.SafeLoader)


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
    # logging.debug(f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}")

    for item in response.json()['hits']['hits']:
        logging.debug(f"Loading data from document ID {item['_id']} with field id={item['_source']['id'] if 'id' in item['_source'] else None} or parameters.run={item['_source']['parameters']['run'] if 'run' in item['_source']['parameters'] else None}")
        tmpfile = tempfile.NamedTemporaryFile(prefix=item['_id'], delete=False).name
        sd = opl.status_data.StatusData(tmpfile, data=item['_source'])
        for path in paths:
            tmp = sd.get(path)
            if tmp is not None:
                out[path].append(tmp)

    logging.debug(f"Loaded {out}")
    return out
