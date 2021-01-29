#!/usr/bin/env python3

import argparse
import datetime
import json
import logging
import os
import sys
import tempfile

import opl.status_data

import requests

import tabulate


def doit_list(args):
    assert args.list_name is not None

    url = f"{args.es_server}/{args.es_index}/_search"
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "name.keyword": args.list_name,
                        },
                    },
                ],
            },
        },
        "sort": {
            "started": {
                "order": "desc",
            },
        },
        "size": args.list_size,
    }

    logging.info(f"Querying ES with url={url}, headers={headers} and json={json.dumps(data)}")

    response = requests.get(url, headers=headers, json=data)
    response.raise_for_status()
    logging.debug(f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}")

    table_headers = [
        'Run ID',
        'Started',
        'Owner',
        'Golden',
        'Result',
    ]
    table = []

    for item in response.json()['hits']['hits']:
        logging.debug(f"Loading data from document ID {item['_id']} with field id={item['_source']['id'] if 'id' in item['_source'] else None}")
        tmpfile = tempfile.NamedTemporaryFile(prefix=item['_id'], delete=False).name
        sd = opl.status_data.StatusData(tmpfile, data=item['_source'])
        table.append([
            sd.get('id'),
            sd.get('started'),
            sd.get('owner'),
            sd.get('golden'),
            sd.get('result'),
        ])

    print(tabulate.tabulate(table, headers=table_headers))


def doit_change(args):
    assert args.change_id is not None

    url = f"{args.es_server}/{args.es_index}/_search"
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "id.keyword": args.change_id,
                        },
                    },
                ],
            },
        },
        "sort": {
            "started": {
                "order": "desc",
            },
        },
        "size": 1,
    }

    logging.info(f"Querying ES with url={url}, headers={headers} and json={json.dumps(data)}")

    response = requests.get(url, headers=headers, json=data)
    response.raise_for_status()
    logging.debug(f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}")

    source = response.json()['hits']['hits'][0]
    es_type = source['_type']
    es_id = source['_id']
    logging.debug(f"Loading data from document ID {source['_id']} with field id={source['_source']['id']}")
    tmpfile = tempfile.NamedTemporaryFile(prefix=source['_id'], delete=False).name
    sd = opl.status_data.StatusData(tmpfile, data=source['_source'])

    for item in args.change_set:
        if item == '':
            logging.warning("Got empty key=value pair to set - ignoring it")
            continue

        key, value = item.split('=')

        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

        logging.debug(f"Setting {key} = {value} ({type(value)})")
        sd.set(key, value)

    # Add comment to log the change
    if sd.get('comments') is None:
        sd.set('comments', [])
    if not isinstance(sd.get('comments'), list):
        logging.error(f"Field 'comments' is not a list: {sd.get('comments')}")
    if args.change_comment_text is None:
        args.change_comment_text = 'Setting ' + ', '.join(args.change_set)
    sd.get('comments').append({
        'author': os.getenv('USER', 'unknown'),
        'date': datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
        'text': args.change_comment_text,
    })

    url = f"{args.es_server}/{args.es_index}/{es_type}/{es_id}"

    logging.info(f"Saving to ES with url={url} and json={json.dumps(sd.dump())}")

    response = requests.post(url, json=sd.dump())
    response.raise_for_status()
    logging.debug(f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}")

    print(sd.info())


def main():
    parser = argparse.ArgumentParser(
        description='Investigate and modify status data documents in ElasticSearch',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--action', required=True,
                        choices=['list', 'change'],
                        help='What action to do')
    parser.add_argument('--es-server',
                        default='http://elasticsearch.example.com:9286',
                        help='ElasticSearch server for the results data')
    parser.add_argument('--es-index', default='my-index',
                        help='ElasticSearch index for the results data')
    parser.add_argument('--list-name',
                        help='Name of the test to query for when listing')
    parser.add_argument('--list-size', type=int, default=50,
                        help='Number of documents to show when listing')
    parser.add_argument('--change-id',
                        help='ID of a test run when changing')
    parser.add_argument('--change-set', nargs='*', default=[],
                        help='Set key=value data')
    parser.add_argument('--change-comment-text',
                        help='Comment to be added as part of change')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug output')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    if args.action == 'list':
        return doit_list(args)
    if args.action == 'change':
        return doit_change(args)
