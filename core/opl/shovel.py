import argparse
import logging
import requests
import json
import os
import re

from . import skelet, status_data


class pluginProw:
    def __init__(self, args):
        self.logger = logging.getLogger("opl.showel.pluginProw")
        self.args = args

    def list(self):
        response = requests.get(f"{self.args.prow_base_url}/{self.args.prow_job_name}")
        # Extract 19-digit numbers using regular expression
        numbers = re.findall(r"\b[0-9]{19}\b", response.text)
        # Sort the numbers in natural order and get the last 10 unique numbers
        sorted_numbers = sorted(set(numbers), key=lambda x: int(x))
        last_10_numbers = sorted_numbers[-10:]
        return last_10_numbers

    def download(self):
        from_url = f"{self.args.prow_base_url}/{self.args.prow_job_name}/{self.args.prow_test_name}/{self.args.prow_artifact_path}"
        to_path = f"{self.args.prow_data_file}"
        if not os.path.isfile(to_path):
            logging.info(f"INFO: Downloading {from_url} ... ")
            response = requests.get(f"{from_url}")
            with open(to_path, "w") as f:
                f.write(json.dumps(response.json()))
            logging.info("DONE")
        else:
            logging.info(f"DEBUG: File {to_path} already present, skipping download")

    @staticmethod
    def set_args(parser, group_actions):
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
        group.add_argument("--prow-data-file", help="prow data json file")


class pluginOpenSearch:
    def __init__(self, args):
        self.logger = logging.getLogger("opl.showel.pluginOpenSearch")
        self.args = args

    def upload(self):
        if self.args.data_file is None:
            raise Exception("A Data file is needed to work with --opensearch-upload")
        elif self.args.matcher_field is None:
            raise Exception("Matcher field is needed to work with --opensearch-upload")
        elif self.args.matcher_field_value is None:
            raise Exception(
                "Matcher field value is needed to work with --opensearch-upload"
            )
        else:
            json_data = json.dumps(
                {
                    "query": {
                        "match": {
                            f"{self.args.matcher_field}": self.args.matcher_field_value
                        }
                    }
                }
            )
            headers = {"Content-Type": "application/json"}
            jsonFile = open(self.args.data_file, "r")
            values = json.load(jsonFile)
            current_doc_in_es = requests.get(
                f"{self.args.es_host_url}/{self.args.es_index}/_search",
                headers=headers,
                data=json_data,
            )
            if json.loads(current_doc_in_es.text)["hits"]["total"]["value"] == 0:
                logging.info("Uploading to ES...")
                requests.post(
                    f"{self.args.es_host_url}/{self.args.es_index}/_doc",
                    headers=headers,
                    data=json.dumps(values),
                )
            else:
                logging.info("INFO: Already in ES, skipping upload")

    @staticmethod
    def set_args(parser, group_actions):
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
        group.add_argument(
            "--matcher-field",
            help="json field which will be used for checking if data exists in ES or not",
        )
        group.add_argument("--matcher-field-value", help="value of the matcher field")


class pluginHorreum:
    def __init__(self, args):
        self.logger = logging.getLogger("opl.showel.pluginHorreum")
        self.args = args

    def upload(self):
        if self.args.horreum_data_file is None:
            raise Exception(
                "Horreum data file is required to work with --horreum-upload"
            )
        elif self.args.horreum_host is None:
            raise Exception("Horreum host is required to work with --horreum-upload")
        elif self.args.token is None:
            raise Exception(
                "Authorisation Token is required to work with --horreum-upload"
            )
        elif self.args.job_name is None:
            raise Exception("Job name is required to work with --horreum-upload")
        elif self.args.test_start is None:
            raise Exception("Test start is required to work with --horreum-upload")
        elif self.args.test_end is None:
            raise Exception("Test end is required to work with --horreum-upload")
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.args.token}",
            }
            jsonFile = open(self.args.horreum_data_file, "r")
            values = json.load(jsonFile)
            jsonFile.close()
            test_matcher = values[self.args.test_job_matcher]
            response = requests.get(
                f"{self.args.horreum_host}/api/test/byName/{self.args.test_name_horreum}",
                headers=headers,
            )
            test_id = json.load(response.text)["id"]
            filter_data = {f"{self.args.test_matcher}": f"{test_matcher}"}
            response = requests.get(
                f"{self.args.horreum_host}/api/dataset/list/{test_id}",
                headers=headers,
                params={"filter": json.dumps(filter_data)},
            )
            datasets = response.json().get("datasets", [])
            if len(datasets) > 0:
                raise Exception(
                    f"Test result {self.args.test_matcher}={test_matcher} found in Horreum {datasets}, skipping upload"
                )
            logging.info("INFO: Uploading to Horreum ... ")
            params = {
                "test": self.args.test_name_horreum,
                "start": self.args.test_start,
                "stop": self.args.test_end,
                "owner": self.args.test_owner,
                "access": self.args.test_access,
            }
            requests.post(
                f"{self.args.horreum_host}/api/run/data",
                params=params,
                headers=headers,
                data=json.dumps(values),
            )

    def result(self):
        if self.args.id_array is None:
            raise Exception(
                "Id array json file is needed to work with --horreum-result"
            )
        elif self.args.horreum_data_file is None:
            raise Exception(
                "Horreum data file is required to work with --horreum-result"
            )
        elif self.args.test_start is None:
            raise Exception("Test start is required to work with --horreum-result")
        elif self.args.test_end is None:
            raise Exception("Test end is required to work with --horreum-result")
        elif self.args.test_id is None:
            raise Exception("Test id is required to work with --horreum-result")
        else:
            values = requests.get(
                f"https://{self.args.horreum_host}/api/alerting/variables",
                params={"test": self.args.test_id},
            )
            id_array = values.json()
            is_fail = 0
            for i in id_array:
                id_value = i["id"]
                jsonFile = open(self.args.horreum_data_file, "r")
                values = json.load(jsonFile)
                jsonFile.close()
                range_data = {
                    "range": {
                        "from": self.args.test_start,
                        "to": self.args.test_end,
                        "oneBeforeAndAfter": True,
                    },
                    "annotation": {"query": id_value},
                }

                # Send a POST request to the API and retrieve the result using curl and jq
                result = requests.get(
                    f"https://{self.args.horreum_host}/api/changes/annotations",
                    headers={"content-type: application/json"},
                    data=json.dumps(range_data),
                )

                # Check if the result is not an empty list
                if result != "[]":
                    is_fail = 1
                    status_data.doit_set(
                        self.args.horreum_data_file, {"result": "FAIL"}
                    )
                    break
            if is_fail != 1:
                status_data.doit_set(self.args.horreum_data_file, {"result": "PASS"})

    @staticmethod
    def set_args(parser, group_actions):
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
        group.add_argument("--test-start", help="time when the test started")
        group.add_argument("--test-end", help="time when the test ended")
        group.add_argument(
            "--test-id", help="Id of the test for which we want to check Pass or Fail"
        )


class pluginResultsDashboard:
    def __init__(self, args):
        self.logger = logging.getLogger("opl.showel.pluginResultsDashboard")
        self.args = args

    def upload(self):
        if self.args.status_data is None:
            raise Exception(
                "Status data file is mandatory to work with --results-dashboard-upload"
            )
        elif self.args.es_host_url is None:
            raise Exception(
                "ES host url is required to work with --results-dashboard-upload"
            )
        elif self.args.group_name is None:
            raise Exception(
                "Group Name is mandatory to work with --results-dashboard-upload"
            )
        elif self.args.product_name is None:
            raise Exception(
                "Product Name is mandatory to work with --results-dashboard-upload"
            )
        elif self.args.test_name is None:
            raise Exception(
                "Test Name is mandatory to work with --results-dashboard-upload"
            )
        else:
            jsonFile = open(self.args.status_data, "r")
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
                f"{self.args.es_host_url}/{self.args.dashboard_es_index}/_search",
                headers=headers,
                data=json_data,
            )
            if json.loads(current_doc_in_es.text)["hits"]["total"]["value"] == 0:
                logging.info("Uploading to results dashboard")
                upload_data = json.dumps(
                    {
                        "date": date,
                        "group": self.args.group_name,
                        "link": link,
                        "product": self.args.product_name,
                        "release": self.args.release,
                        "result": result,
                        "result_id": result_id,
                        "test": self.args.test_name,
                        "version": self.args.version,
                    }
                )
                requests.post(
                    f"{self.args.es_host_url}/{self.args.dashboard_es_index}/_doc",
                    headers=headers,
                    data=upload_data,
                )
            else:
                logging.info("INFO: Already in Results Dashboard ES, skipping upload")

    @staticmethod
    def set_args(parser, group_actions):
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
        plugin.set_args(parser, group_actions)

    with skelet.test_setup(parser) as (args, status_data):
        logger = logging.getLogger("main")
        for plugin_name, function_name in args.actions:
            logger.info(
                f"Instantiating plugin {plugin_name} for function {function_name}"
            )
            plugin_object = PLUGINS[plugin_name]
            plugin_instance = plugin_object(args)
            getattr(plugin_instance, function_name)()
