import argparse
import logging
import requests
import json
import subprocess
import os

from . import skelet, status_data


class pluginProw:
    def __init__(self, args):
        print("Hello from pluginProw init 2")
        self.logger = logging.getLogger("opl.showel.pluginProw")

    def list(self):
        print("Hi from pluginProw list")

    def download(self, args):
        from_url = f"{args.prow_base_url}/{args.prow_job_name}/{args.prow_test_name}/{args.prow_artifact_path}"
        to_path = f"{args.prow_data_file}"
        if not os.path.isfile(to_path):
            print(f"INFO: Downloading {from_url} ... ", end="")
            subprocess.run(["curl", "-Ssl", "-o", to_path, from_url], check=True)
            print("DONE")
        else:
            print(f"DEBUG: File {to_path} already present, skipping download")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--prow-list",
            dest="actions",
            default=[],
            action="append_const",
            const=("prow", "list"),
            help="List runs for specific Prow run",
        )
        group_actions.add_argument(
            "--prow-download",
            dest="actions",
            default=[],
            action="append_const",
            const=("prow", "download"),
            help="Download file from Prow run artifacts",
        )

        group = parser.add_argument_group(
            title="prow",
            description="Options needed to work with Prow",
        )
        group.add_argument(
            "--prow-base-url",
            default="https://gcsweb-ci.apps.ci.l2s4.p1.openshiftapps.com/gcs/origin-ci-test/logs/",
            help="Base URL",
        )
        group.add_argument(
            "--prow-job-name",
            default="periodic-ci-redhat-appstudio-e2e-tests-load-test-ci-daily-10u-10t",
            help="Job name as available in ci-operator/jobs/...",
        )
        group.add_argument(
            "--prow-test-name",
            default="load-test-ci-daily-10u-10t",
            help="Test name as configured in ci-operator/config/...",
        )
        group.add_argument(
            "--prow-artifact-path",
            default="redhat-appstudio-load-test/artifacts/load-tests.json",
            help="Path to the artifact",
        )
        group.add_argument("--prow-data-file", help="prow data jdon file")


class pluginOpenSearch:
    def __init__(self, args):
        print("Hello from pluginOpenSearch init")
        self.logger = logging.getLogger("opl.showel.pluginOpenSearch")

    def upload(self, args):
        print("Hello from pluginOpenSearch upload")
        if args.data_file is None:
            raise Exception("A Data file is needed to work with --opensearch-upload")
        elif args.end_timestamp is None:
            raise Exception("End timestamp is needed to work with --opensearch-upload")
        else:
            json_data = json.dumps(
                {"query": {"match": {"endTimestamp": args.end_timestamp}}}
            )
            headers = {"Content-Type": "application/json"}
            jsonFile = open(args.data_file, "r")
            values = json.load(jsonFile)
            current_doc_in_es = requests.get(
                f"{args.es_host_url}/{args.es_index}/_search",
                headers=headers,
                data=json_data,
            )
            if json.loads(current_doc_in_es.text)["hits"]["total"]["value"] == 0:
                print("Uploading to ES...")
                requests.post(
                    f"{args.es_host_url}/{args.es_index}/_doc",
                    headers=headers,
                    data=json.dumps(values),
                )
            else:
                print("INFO: Already in ES, skipping upload")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--opensearch-upload",
            dest="actions",
            default=[],
            action="append_const",
            const=("opensearch", "upload"),
            help="Upload file to OpenSearch if not already there",
        )

        group = parser.add_argument_group(
            title="opensearch",
            description="Options needed to work with OpenSearch",
        )
        group.add_argument(
            "--es-index",
            default="rhtap-ci-status-data",
            help="Elastic search index where the data will be stored",
        )
        group.add_argument("--data-file", help="json file to upload to elastic search")
        group.add_argument("--end-timestamp", help="timestamp when the test ended")


class pluginHorreum:
    def __init__(self, args):
        print("Hello from pluginHorreum init")
        self.logger = logging.getLogger("opl.showel.pluginHorreum")

    def upload(self, args):
        if args.horreum_data_file is None:
            raise Exception(
                "Horreum data file is required to work with --horreum-upload"
            )
        elif args.horreum_host is None:
            raise Exception("Horreum host is required to work with --horreum-upload")
        elif args.token is None:
            raise Exception(
                "Authorisation Token is required to work with --horreum-upload"
            )
        elif args.job_name is None:
            raise Exception("Job name is required to work with --horreum-upload")
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {args.token}",
            }
            jsonFile = open(args.horreum_data_file, "r")
            values = json.load(jsonFile)
            jsonFile.close()
            test_matcher = values[args.test_job_matcher]
            test_start = values["timestamp"]
            if test_start == "None":
                test_start = values["startTimestamp"]
            test_end = values["endTimestamp"]
            if (
                not test_start
                or not test_end
                or test_start == "None"
                or test_end == "None"
            ):
                raise Exception(
                    "ERROR: We need start and end time in the JSON we are supposed to upload"
                )
            response = requests.get(
                f"{args.horreum_host}/api/test/byName/{args.test_name_horreum}",
                headers=headers,
            )
            test_id = json.load(response.text)["id"]
            page = 0
            while True:
                data = {
                    "from": page,
                    "size": 100,
                    "sort": [{"date": {"order": "desc"}}],
                }
                page_data = requests.get(
                    f"{args.horreum_host}/api/run/list/{test_id}",
                    headers=headers,
                    data=data,
                )
                page = page + 100
                try:
                    json.loads(page_data)
                except ValueError as e:
                    raise Exception(e)
                page_data_values = json.loads(page_data)
                page_data_len = len(page_data_values["runs"])
                if page_data_len == 0:
                    print(
                        "INFO: No more Horreum test results to review, proceeding with upload"
                    )
                    break
                for runs in page_data_values["runs"]:
                    test_run_id = runs["id"]
                    test_run_data = requests.get(
                        f"{args.horreum_host}/api/run/{test_run_id}"
                    )
                    try:
                        json.loads(test_run_data)
                    except ValueError as e:
                        raise Exception(e)
                    test_run_data_values = json.loads(test_run_data)
                    test_run_matcher = test_run_data_values["data"][
                        args.test_job_matcher
                    ]
                    if test_run_matcher == "null":
                        print(
                            f"WARNING: Test run {test_run_id} for test {args.test_name_horreum}/{test_id} does not have {args.test_job_matcher}, skipping"
                        )
                        continue
                    if test_matcher == test_run_matcher:
                        raise Exception(
                            "INFO: Test result found in Horreum, skipping upload"
                        )

            print("INFO: Uploading to Horreum ... ")
            params = {
                "test": args.test_name_horreum,
                "start": test_start,
                "stop": test_end,
                "owner": args.test_owner,
                "access": args.test_access,
            }
            requests.post(
                f"{args.horreum_host}/api/run/data",
                params=params,
                headers=headers,
                data=json.dumps(values),
            )

    def result(self, args):
        print("Hello from pluginHorreum result")
        if args.id_array is None:
            raise Exception(
                "Id array json file is needed to work with --horreum-result"
            )
        elif args.horreum_data_file is None:
            raise Exception(
                "Horreum data file is required to work with --horreum-result"
            )
        else:
            values = json.loads(args.id_array)
            is_fail = 0
            for i in values:
                id_value = i["id"]
                jsonFile = open(args.horreum_data_file, "r")
                values = json.load(jsonFile)
                jsonFile.close()
                test_start = values["timestamp"]
                if test_start == "None":
                    test_start = values["startTimestamp"]
                test_end = values["endTimestamp"]
                range_data = {
                    "range": {
                        "from": test_start,
                        "to": test_end,
                        "oneBeforeAndAfter": True,
                    }
                }

                # Create a dictionary with the annotation query
                annotation_data = {"annotation": {"query": id_value}}

                # Write the range data to a JSON file
                with open("/tmp/annotationQuery.json", "w") as file:
                    json.dump(range_data, file)

                # Append the annotation data to the JSON file
                with open("/tmp/annotationQuery.json", "a") as file:
                    json.dump(annotation_data, file)

                # Send a POST request to the API and retrieve the result using curl and jq
                curl_command = f"curl https://{args.horreum_host}/api/changes/annotations -s -H 'content-type: application/json' -d @/tmp/annotationQuery.json | jq -r ."
                result = (
                    subprocess.check_output(curl_command, shell=True)
                    .decode("utf-8")
                    .strip()
                )

                # Check if the result is not an empty list
                if result != "[]":
                    is_fail = 1
                    status_data.doit_set(args.horreum_data_file, {"result": "FAIL"})
                    break
            if is_fail != 1:
                status_data.doit_set(args.horreum_data_file, {"result": "PASS"})

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--horreum-upload",
            dest="actions",
            default=[],
            action="append_const",
            const=("horreum", "upload"),
            help="Upload file to Horreum if not already there",
        )
        group_actions.add_argument(
            "--horreum-result",
            dest="actions",
            default=[],
            action="append_const",
            const=("horreum", "result"),
            help="Get Horreum no-/change signal for a given time range",
        )

        group = parser.add_argument_group(
            title="horreum",
            description="Options needed to work with Horreum",
        )
        group.add_argument("--horreum-data-file", help="Data file to upload to Horreum")
        group.add_argument("--horreum-host", help="Horreum host url")
        group.add_argument("--token", help="Authorisation token")
        group.add_argument("--job-name", help="Job name")
        group.add_argument(
            "--test-name-horreum", default="load-tests-result", help="Test Name"
        )
        group.add_argument("--test-job-matcher", default="jobName")
        group.add_argument("--test-owner", default="rhtap-perf-test-team")
        group.add_argument("--test-access", default="PUBLIC")
        group.add_argument(
            "--id-array", help="Variable id array we wish to get timeseries data for"
        )


class pluginResultsDashboard:
    def __init__(self, args):
        print("Hello from pluginResultsDashboard init")
        self.logger = logging.getLogger("opl.showel.pluginResultsDashboard")

    def upload(self, args):
        print("Hello from pluginResultsDashboard upload")
        if args.status_data is None:
            raise Exception(
                "Status data file is mandatory to work with --results-dashboard-upload"
            )
        elif args.es_host_url is None:
            raise Exception(
                "ES host url is required to work with --results-dashboard-upload"
            )
        elif args.group_name is None:
            raise Exception(
                "Group Name is mandatory to work with --results-dashboard-upload"
            )
        elif args.product_name is None:
            raise Exception(
                "Product Name is mandatory to work with --results-dashboard-upload"
            )
        elif args.test_name is None:
            raise Exception(
                "Test Name is mandatory to work with --results-dashboard-upload"
            )
        else:
            jsonFile = open(args.status_data, "r")
            values = json.load(jsonFile)
            jsonFile.close()
            date = values["timestamp"]
            link = values["jobLink"]
            result = values["result"]
            result_id = values["metadata"]["env"]["BUILD_ID"]
            json_data = json.dumps(
                {
                    "query": {
                        "bool": {
                            "filter": [{"term": {"result_id.keyword": f"{result_id}"}}]
                        }
                    }
                }
            )
            headers = {"Content-Type": "application/json"}
            current_doc_in_es = requests.get(
                f"{args.es_host_url}/{args.dashboard_es_index}/_search",
                headers=headers,
                data=json_data,
            )
            if json.loads(current_doc_in_es.text)["hits"]["total"]["value"] == 0:
                print("Uploading to results dashboard")
                upload_data = json.dumps(
                    {
                        "date": date,
                        "group": args.group_name,
                        "link": link,
                        "product": args.product_name,
                        "release": args.release,
                        "result": result,
                        "result_id": result_id,
                        "test": args.test_name,
                        "version": args.version,
                    }
                )
                requests.post(
                    f"{args.es_host_url}/{args.dashboard_es_index}/_doc",
                    headers=headers,
                    data=upload_data,
                )
            else:
                print("INFO: Already in Results Dashboard ES, skipping upload")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--resultsdashboard-upload",
            dest="actions",
            default=[],
            action="append_const",
            const=("resultsdashboard", "upload"),
            help="Upload file to Results Dashboard if not already there",
        )
        group = parser.add_argument_group(
            title="resultsdashboard",
            description="Options needed to work with Results Dashboard",
        )
        group.add_argument(
            "--es-host-url",
            help="Elastic search host url",
        )
        group.add_argument(
            "--dashboard-es-index",
            default="results-dashboard-data",
            help="Elastic search index where the result is stored",
        )
        group.add_argument(
            "--status-data",
            help="File where we maintain metadata, results, parameters and measurements for this test run",
        )
        group.add_argument(
            "--group-name", help="Name of the group where the product belongs"
        )
        group.add_argument("--product-name", help="Name of the Product")
        group.add_argument(
            "--release",
            default="latest",
            help="Type of release of Product for e.g latest,nightly,weekly",
        )
        group.add_argument("--test-name", help="Name of the CPT test")
        group.add_argument(
            "--version",
            default="1",
            help="Version of the product on which the test ran",
        )


PLUGINS = {
    "prow": pluginProw,
    "opensearch": pluginOpenSearch,
    "horreum": pluginHorreum,
    "resultsdashboard": pluginResultsDashboard,
}


def main():
    parser = argparse.ArgumentParser(
        description="Shovel data from A to B",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group_actions = parser.add_argument_group(
        title="actions",
        description="Various high level things you can do",
    )
    for name, plugin in PLUGINS.items():
        plugin.args(parser, group_actions)

    with skelet.test_setup(parser) as (args, status_data):
        logger = logging.getLogger("main")
        for plugin_name, function_name in args.actions:
            logger.info(
                f"Instantiating plugin {plugin_name} for function {function_name}"
            )
            plugin_object = PLUGINS[plugin_name]
            plugin_instance = plugin_object(args)
            getattr(plugin_instance, function_name)(args)
