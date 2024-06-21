#!/usr/bin/env python3

import argparse
import datetime
import json
import logging
import os
import random
import tempfile
import time
from collections import OrderedDict

from opl.status import StatusData

import requests
import requests.adapters

import tabulate

import urllib3

import yaml


RP_TO_ES_STATE = {
    "automation_bug": "FAIL",
    "no_defect": "PASS",
    "product_bug": "FAIL",
    "system_issue": "ERROR",
    "to_investigate": "FAIL",
}

STATE_WEIGHTS = {
    "PASS": 0,
    "FAIL": 1,
    "ERROR": 2,
}


def get_session():
    session = requests.Session()
    retry_adapter = requests.adapters.HTTPAdapter(
        max_retries=urllib3.Retry(total=None, connect=10, backoff_factor=1)
    )
    session.mount("https://", retry_adapter)
    session.mount("http://", retry_adapter)
    return session


def _es_get_test(session, args, key, val, size=1, sort_by="started"):
    url = f"{args.es_server}/{args.es_index}/_search"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "query": {
            "bool": {
                "filter": [],
            },
        },
        "sort": {
            sort_by: {
                "order": "desc",
            },
        },
        "size": size,
    }

    for k, v in zip(key, val):
        data["query"]["bool"]["filter"].append(
            {
                "term": {
                    k: v,
                },
            }
        )

    if session is None:
        session = get_session()

    logging.info(
        f"Querying ES with url={url}, headers={headers} and json={json.dumps(data)}"
    )
    attempt = 0
    attempt_max = 10
    while True:
        try:
            response = session.get(url, headers=headers, json=data)
        except requests.exceptions.ConnectionError:
            if attempt >= attempt_max:
                raise
            attempt += 1
            time.sleep(attempt)
        else:
            break
    response.raise_for_status()
    logging.debug(
        f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}"
    )

    return response.json()


def _add_comment(args, sd, author=None, text=None):
    """Add text as a comment to status data document."""
    if sd.get("comments") is None:
        sd.set("comments", [])

    if not isinstance(sd.get("comments"), list):
        logging.error(f"Field 'comments' is not a list: {sd.get('comments')}")

    if author is None:
        author = os.getenv("USER", "unknown")
    if text is None:
        text = "Setting " + ", ".join(args.change_set)

    sd.get("comments").append(
        {
            "author": author,
            "date": datetime.datetime.utcnow()
            .replace(tzinfo=datetime.timezone.utc)
            .isoformat(),
            "text": text,
        }
    )


def doit_list(args):
    assert args.list_name is not None

    response = _es_get_test(
        None, args, ["name.keyword"], [args.list_name], args.list_size
    )

    table_headers = [
        "Run ID",
        "Started",
        "Owner",
        "Golden",
        "Result",
    ] + args.list_fields
    table = []

    for item in response["hits"]["hits"]:
        sd = _create_sd_from_es_response(item)
        row = [
            sd.get("id"),
            sd.get("started"),
            sd.get("owner"),
            sd.get("golden"),
            sd.get("result"),
        ]
        row += [sd.get(i) for i in args.list_fields]
        table.append(row)

    print(tabulate.tabulate(table, headers=table_headers))


def doit_change(args):
    assert args.change_id is not None

    response = _es_get_test(None, args, ["id.keyword"], [args.change_id])

    source = response["hits"]["hits"][0]
    es_type = source["_type"]
    es_id = source["_id"]
    sd = _create_sd_from_es_response(source)

    for item in args.change_set:
        if item == "":
            logging.warning("Got empty key=value pair to set - ignoring it")
            continue

        key, value = item.split("=")

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
    _add_comment(args, sd, text=args.change_comment_text)

    url = f"{args.es_server}/{args.es_index}/{es_type}/{es_id}"

    logging.info(f"Saving to ES with url={url} and json={json.dumps(sd.dump())}")

    if args.dry_run:
        logging.info("Not touching ES as we are running in dry run mode")
    else:
        response = requests.post(url, json=sd.dump())
        response.raise_for_status()
        logging.debug(
            f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}"
        )

    print(sd.info())


def _get_rp_launches(session, args, rp_launch=None, rp_launches_count=None):
    """Get N newest launches from RP"""
    if rp_launch is None:
        rp_launch = args.rp_launch
    if rp_launches_count is None:
        rp_launches_count = args.rp_launches_count

    url = f"https://{args.rp_host}/api/v1/{args.rp_project}/launch"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.rp_token}",
    }
    data = {
        "filter.eq.name": rp_launch,
        "page.size": rp_launches_count,
        "page.sort": "endTime,desc",
    }
    logging.debug(f"Going to do GET request to {url} with {data}")
    response = session.get(
        url, params=data, headers=headers, verify=not args.rp_noverify
    )
    if not response.ok:
        logging.error(f"Request failed: {response.text}")
    response.raise_for_status()
    logging.debug(f"Request returned {response.json()}")
    return response.json()["content"]


def _get_run_id_from_rp_launch(launch):
    """Return "run_id" attribute value from RP launch or None if not present"""
    run_id = None
    for a in launch["attributes"]:
        if a["key"] == "run_id":
            run_id = a["value"]
            break
    return run_id


def _filter_rp_launches_without_run_id(launches):
    """Filter out RP launches that does not have "run_id" attribute"""
    launches_filtered = []
    for launch in launches:
        run_id = _get_run_id_from_rp_launch(launch)
        if run_id is None:
            logging.warning(
                f"Launch id={launch['id']} do not have run_id attribute, skipping it"
            )
            continue
        launches_filtered.append(launch)
    return launches_filtered


def _get_rp_launch_results(session, args, launch):
    """Get results for RP launch"""
    results = []
    url = f"https://{args.rp_host}/api/v1/{args.rp_project}/item"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.rp_token}",
    }
    data = {
        "filter.eq.launchId": launch["id"],
        "filter.eq.type": "TEST",
        "filter.ne.status": "PASSED",
        "page.size": 100,
        "page.page": 0,
        "page.sort": "id,asc",
    }
    while True:
        logging.debug(f"Going to do GET request to {url} with {data}")
        response = session.get(
            url, params=data, headers=headers, verify=not args.rp_noverify
        )
        results += response.json()["content"]
        if response.json()["page"]["number"] < response.json()["page"]["totalPages"]:
            data["page.page"] += 1
        else:
            logging.debug(
                "No content in the response, considering this last page of data"
            )
            break
    logging.debug(f"OK, we have {len(results)} results from RP for this launch")
    return results


def _create_sd_from_es_response(response):
    """Convert ElasticSearch response data structure to StatusData object."""
    logging.debug(
        f"Loading data from document ID {response['_id']} with field id={response['_source']['id'] if 'id' in response['_source'] else None}"
    )
    tmpfile = tempfile.NamedTemporaryFile(prefix=response["_id"], delete=False).name
    return StatusData(tmpfile, data=response["_source"])


def _get_es_result_for_rp_result(session, args, run_id, result):
    if args.rp_project == "satcpt":
        # OK, I agree we need a better way here.
        # In all projects except SatCPT we have 1 run_id for 1 test
        # result, but in SatCPT we need to differentiate by name as
        # well and that is composed differently in SatCPT and in other
        # CPTs :-(
        if "itemPaths" not in result["pathNames"]:
            raise Exception(
                f"This result do not have result -> pathNames -> itemPaths, skipping it: {result}"
            )
        else:
            sd_name = f"{result['pathNames']['itemPaths'][0]['name']}/{result['name']}"
            response = _es_get_test(
                session, args, ["id.keyword", "name.keyword"], [run_id, sd_name]
            )
    elif args.rp_project == "aapcpt":
        response = _es_get_test(
            session, args, ["id.keyword", "name.keyword"], [run_id, result["name"]]
        )
    else:
        response = _es_get_test(session, args, ["id.keyword"], [run_id])
        assert response["hits"]["total"]["value"] == 1
    try:
        source = response["hits"]["hits"][0]
    except IndexError:
        raise Exception(f"Failed to find test result in ES for {run_id}")
    es_type = source["_type"]
    es_id = source["_id"]
    sd = _create_sd_from_es_response(source)
    return (sd, es_type, es_id)


def _get_es_dashboard_result_for_run_id(session, args, run_id, test=None):
    if test is not None:
        response = _es_get_test(
            session,
            args,
            ["result_id.keyword", "test.keyword"],
            [run_id, test],
            sort_by="date",
        )
    else:
        response = _es_get_test(
            session, args, ["result_id.keyword"], [run_id], sort_by="date"
        )
    if response["hits"]["total"]["value"] == 0:
        return (None, None, None)
    else:
        assert (
            response["hits"]["total"]["value"] == 1
        ), "There have to be exactly one result"
    try:
        source = response["hits"]["hits"][0]
    except IndexError:
        logging.debug(f"Failed to find dashboard result in ES for {run_id}")
        return (None, None, None)
    else:
        return (response["hits"]["hits"][0]["_source"], source["_type"], source["_id"])


def _get_rp_result_defect_string(result):
    return list(result["statistics"]["defects"].keys())[0]


def _get_rp_result_result_string(result):
    return RP_TO_ES_STATE[_get_rp_result_defect_string(result)]


def doit_rp_to_es(args):
    assert args.es_server is not None
    assert args.rp_host is not None

    stats = {
        "launches": 0,
        "cases": 0,
        "cases_changed": 0,
    }

    if args.rp_noverify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Start a session
    session = get_session()

    # Get 10 newest launches
    launches = _get_rp_launches(session, args)

    # Filter out RP launches that does not have "run_id" attribute
    launches = _filter_rp_launches_without_run_id(launches)

    for launch in launches:
        stats["launches"] += 1

        # Get run ID from launch attributes
        run_id = _get_run_id_from_rp_launch(launch)

        # Get test results from launch
        results = _get_rp_launch_results(session, args, launch)
        print(f"Going to compare {len(results)} results for launch {launch['id']}")

        # Process individual results
        for result in results:
            logging.debug(f"Processing RP result {result}")
            stats["cases"] += 1

            # Get resuls from launch statistics
            result_string = _get_rp_result_result_string(result)

            # Get relevant status data document from ElasticSearch
            try:
                sd, es_type, es_id = _get_es_result_for_rp_result(
                    session, args, run_id, result
                )
            except Exception as e:
                logging.warning(
                    f"Something went wrong when getting data for {run_id}/{result}: {e}"
                )
                continue

            logging.debug(
                f"Comparing result from RP {result_string} to result from ES {sd.get('result')}"
            )
            if sd.get("result") != result_string:
                stats["cases_changed"] += 1

                # Add comment to log the change
                try:
                    comment = "Comment from RP: " + result["issue"]["issueType"]
                except IndexError:
                    comment = f"Automatic update as per ReportPortal change: {sd.get('result')} -> {result_string}"
                _add_comment(args, sd, author="status_data_updater", text=comment)

                logging.info(
                    f"Results do not match, updating them: {sd.get('result')} != {result_string}"
                )
                sd.set("result", result_string)

                # Save the changes to ES
                url = f"{args.es_server}/{args.es_index}/{es_type}/{es_id}"
                logging.info(
                    f"Saving to ES with url={url} and json={json.dumps(sd.dump())}"
                )
                if args.dry_run:
                    logging.info("Not touching ES as we are running in dry run mode")
                else:
                    attempt = 0
                    attempt_max = 10
                    while True:
                        response = session.post(url, json=sd.dump())
                        if (
                            response.status_code == 429
                        ):  # 429 Client Error: Too Many Requests for url: http://.../<index>/_doc/...
                            attempt += 1
                            if attempt >= attempt_max:
                                raise Exception(
                                    f"Failed to update data in ES after {attempt} attempts: {response}"
                                )
                            else:
                                logging.info(
                                    f"Request failed with '429 Client Error: Too Many Requests'. Will retry in a bit. Attempt {attempt}/{attempt_max}"
                                )
                                time.sleep(random.randint(1, 10))
                        else:
                            break
                    response.raise_for_status()
                    logging.debug(
                        f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}"
                    )

    print(tabulate.tabulate(stats.items()))


def doit_rp_to_dashboard_new(args):
    assert args.es_server is not None

    if args.rp_noverify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Start a session
    session = get_session()

    run_id = args.dashboard_run_id
    result = args.dashboard_result

    if not args.dashboard_skip_uniqness_check:
        # Ensure there are no results for this run_id in ElasticSearch yet
        try:
            dashboard, es_type, es_id = _get_es_dashboard_result_for_run_id(
                session, args, run_id
            )
        except requests.exceptions.HTTPError as e:
            matching = (
                "No mapping found for [date] in order to sort on" in e.response.text
            )
            if e.response.status_code == 400 and matching:
                logging.debug(
                    "Request failed, but I guess it was because index is still empty"
                )
                dashboard = None
            else:
                raise
        assert dashboard is None, f"Result {run_id} already exists: {dashboard}"

    # Create new result in the dashboard
    url = f"{args.es_server}/{args.es_index}/_doc/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.rp_token}",
    }
    data = {
        "result_id": run_id,
        "group": args.dashboard_group,
        "product": args.dashboard_product,
        "release": args.dashboard_release,
        "version": args.dashboard_version,
        "link": args.dashboard_link,
        "test": args.dashboard_test,
        "result": result,
        "date": args.dashboard_date,
    }
    logging.debug(f"Going to do POST request to {url} with {data}")
    response = session.post(
        url, json=data, headers=headers, verify=not args.rp_noverify
    )
    response.raise_for_status()
    logging.debug(
        f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}"
    )
    print(f"Created result {run_id} in the dashboard with value {result}")


def _update_es_dashboard_result(session, args, es_id, result_string):
    url = f"{args.es_server}/{args.es_index}/_doc/{es_id}/_update"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.rp_token}",
    }
    data = {
        "doc": {
            "result": result_string,
        },
    }
    logging.debug(f"Going to do POST request to {url} with {data}")
    if args.dry_run:
        logging.debug("Skipped because of dry-run")
    else:
        attempt = 0
        attempt_max = 10
        while True:
            try:
                response = session.post(
                    url, json=data, headers=headers, verify=not args.rp_noverify
                )
            except requests.exceptions.ConnectionError:
                if attempt >= attempt_max:
                    raise
                attempt += 1
                time.sleep(attempt)
            else:
                break
        response.raise_for_status()
        logging.debug(
            f"Got back this: {json.dumps(response.json(), sort_keys=True, indent=4)}"
        )


def doit_rp_to_dashboard_update(args):
    assert args.es_server is not None
    assert args.rp_host is not None

    stats = {
        "launches": 0,
        "results": 0,
        "results_changed": 0,
    }

    if args.rp_noverify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Start a session
    session = requests.Session()

    # Get 10 newest launches
    launches = _get_rp_launches(session, args)

    # Filter out RP launches that does not have "run_id" attribute
    launches = _filter_rp_launches_without_run_id(launches)

    for launch in launches:
        stats["launches"] += 1

        # Get run ID from launch attributes
        run_id = _get_run_id_from_rp_launch(launch)

        # Get test results from launch
        results = _get_rp_launch_results(session, args, launch)
        print(f"Going to compare {len(results)} results for launch {launch['id']}")

        # Process individual results to get final result
        for result in results:
            logging.debug(f"Processing RP result {result}")

            result_string = _get_rp_result_result_string(result)

            # Get relevant dashboard result from ElasticSearch
            dashboard, es_type, es_id = _get_es_dashboard_result_for_run_id(
                session,
                args,
                run_id,
                result["name"],
            )
            if dashboard is None:
                logging.warning(
                    f"Result {run_id} '{result['name']}' does not exist in the dashboard, skipping updating it"
                )
                continue

            # Update the result in dashboard if needed
            stats["results"] += 1
            if dashboard["result"] == result_string:
                pass  # data in the dashboard are correct, no action needed
            else:
                _update_es_dashboard_result(
                    session,
                    args,
                    es_id,
                    result_string,
                )
                stats["results_changed"] += 1

    print(tabulate.tabulate(stats.items()))


def doit_rp_backlog(args):
    assert args.rp_host is not None
    assert args.jobs_ownership_config is not None

    if args.rp_noverify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Start a session
    session = requests.Session()

    with open(args.jobs_ownership_config, "r") as fp:
        launches_to_check = yaml.load(fp, Loader=yaml.Loader)

    data_per_owner = OrderedDict()
    data_per_job = OrderedDict()

    for launch_to_check in launches_to_check:
        rp_launch = launch_to_check["name"]
        rp_launches_count = launch_to_check["history"]
        rp_launch_owner = launch_to_check["owner"]
        if rp_launch_owner not in data_per_owner:
            data_per_owner[rp_launch_owner] = OrderedDict(
                [
                    ("automation_bug", 0),
                    ("no_defect", 0),
                    ("product_bug", 0),
                    ("system_issue", 0),
                    ("to_investigate", 0),
                ]
            )
        if rp_launch not in data_per_job:
            data_per_job[rp_launch] = OrderedDict(
                [
                    ("automation_bug", 0),
                    ("no_defect", 0),
                    ("product_bug", 0),
                    ("system_issue", 0),
                    ("to_investigate", 0),
                ]
            )

        # Get N newest launches
        launches = _get_rp_launches(
            session, args, rp_launch=rp_launch, rp_launches_count=rp_launches_count
        )

        # Filter out RP launches that does not have "run_id" attribute
        launches = _filter_rp_launches_without_run_id(launches)

        for launch in launches:
            # Get run ID for a launch
            run_id = _get_run_id_from_rp_launch(launch)

            # Get test results from launch
            results = _get_rp_launch_results(session, args, launch)
            logging.debug(
                f"Going to compare {len(results)} results for launch {launch['id']}"
            )

            # Process individual results
            for result in results:
                logging.debug(f"Processing RP result {result}")

                # Get resuls from launch statistics
                assert (
                    result["statistics"]["executions"]["total"] == 1
                ), "We only know how to work with results with one executions"
                result_string = result["status"]
                defect_string = _get_rp_result_defect_string(result)
                override_string = _get_rp_result_result_string(result)
                logging.debug(
                    f"Counted result {run_id}: {result_string}, {defect_string}, {override_string}"
                )
                data_per_owner[rp_launch_owner][defect_string] += 1
                data_per_job[rp_launch][defect_string] += 1

    headers = sorted(list(data_per_owner[next(iter(data_per_owner.keys()))].keys()))

    rows = []
    for owner in data_per_owner:
        row = [owner]
        for defect in headers:
            row.append(data_per_owner[owner].get(defect, None))
        rows.append(row)
    print(tabulate.tabulate(rows, headers=headers))

    rows = []
    for job in data_per_job:
        row = [job]
        for defect in headers:
            row.append(data_per_job[job].get(defect, None))
        rows.append(row)
    print(tabulate.tabulate(rows, headers=headers))


def main():
    parser = argparse.ArgumentParser(
        description="Investigate and modify status data documents in ElasticSearch",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "list",
            "change",
            "rp-to-es",
            "rp-to-dashboard-new",
            "rp-to-dashboard-update",
            "rp-backlog",
        ],
        help="What action to do",
    )

    parser.add_argument(
        "--es-server",
        default="http://elasticsearch.example.com:9286",
        help="ElasticSearch server for the results data",
    )
    parser.add_argument(
        "--es-index",
        default="my-index",
        help="ElasticSearch index for the results data",
    )

    parser.add_argument(
        "--list-name", help="Name of the test to query for when listing"
    )
    parser.add_argument(
        "--list-size",
        type=int,
        default=50,
        help="Number of documents to show when listing",
    )
    parser.add_argument(
        "--list-fields",
        nargs="+",
        default=[],
        help="Additional fields to add to the table",
    )

    parser.add_argument("--change-id", help="ID of a test run when changing")
    parser.add_argument(
        "--change-set", nargs="*", default=[], help="Set key=value data"
    )
    parser.add_argument(
        "--change-comment-text", help="Comment to be added as part of change"
    )

    parser.add_argument("--rp-host", help="ReportPortal host")
    parser.add_argument(
        "--rp-noverify",
        action="store_true",
        help="When talking to ReportPortal ignore certificate verification failures",
    )
    parser.add_argument("--rp-project", help="ReportPortal project")
    parser.add_argument("--rp-token", help="ReportPortal token")
    parser.add_argument("--rp-launch", help="ReportPortal launch name")
    parser.add_argument(
        "--rp-launches-count",
        default=10,
        type=int,
        help="Number of ReportPortal launches to load",
    )

    parser.add_argument(
        "--jobs-ownership-config",
        help="YAML config with owners and history size for ReportPortal 'to_investigate' rp-backlog feature",
    )

    parser.add_argument(
        "--dashboard-run-id",
        default="Unknown run_id",
        help="When pushing new result to dashboard, this is the run_id",
    )
    parser.add_argument(
        "--dashboard-result",
        default="ERROR",
        help="When pushing new result to dashboard, this is the result",
    )
    parser.add_argument(
        "--dashboard-test",
        default="N/A",
        help="When pushing new result to dashboard, this is the test name",
    )
    parser.add_argument(
        "--dashboard-group",
        default="Unknown group",
        help="Product group for result dashboard",
    )
    parser.add_argument(
        "--dashboard-product",
        default="Unknown product",
        help="Product for result dashboard",
    )
    parser.add_argument(
        "--dashboard-release",
        default="Unknown release",
        help="Product release stream for result dashboard",
    )
    parser.add_argument(
        "--dashboard-version",
        default="Unknown version",
        help="Application version during the test for result dashboard",
    )
    parser.add_argument(
        "--dashboard-link",
        default="Unknown link",
        help="Link with test details for result dashboard",
    )
    parser.add_argument(
        "--dashboard-date",
        default=datetime.datetime.utcnow()
        .replace(tzinfo=datetime.timezone.utc)
        .isoformat(),
        help="When the test was executed for result dashboard",
    )
    parser.add_argument(
        "--dashboard-skip-uniqness-check",
        action="store_true",
        help="Do not check that result with this run ID exists in result dashboard",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually change data, meant for debugging",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    if args.action == "list":
        return doit_list(args)
    if args.action == "change":
        return doit_change(args)
    if args.action == "rp-to-es":
        return doit_rp_to_es(args)
    if args.action == "rp-to-dashboard-new":
        return doit_rp_to_dashboard_new(args)
    if args.action == "rp-to-dashboard-update":
        return doit_rp_to_dashboard_update(args)
    if args.action == "rp-backlog":
        return doit_rp_backlog(args)
