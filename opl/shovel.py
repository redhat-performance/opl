import argparse
import logging
import requests
import json
import os
import re
import urllib3

from . import skelet, status_data


class pluginProw:
    def __init__(self, args):
        self.logger = logging.getLogger("opl.showel.pluginProw")
        self.args = args

    def list(self):
        response = requests.get(f"{self.args.prow_base_url}/{self.args.prow_job_name}")
        response.raise_for_status()

        # Extract 19-digit numbers using regular expression
        numbers = re.findall(r"\b[0-9]{19}\b", response.text)

        # Sort the numbers in numerical order and get the last 10 unique numbers
        sorted_numbers = sorted(set(numbers), key=lambda x: int(x))
        last_10_numbers = sorted_numbers[-10:]
        for n in last_10_numbers:
            print(n)

    def download(self):
        if os.path.isfile(self.args.prow_data_file):
            print(f"File {self.args.prow_data_file} already present, skipping download")
            return

        from_url = f"{self.args.prow_base_url}/{self.args.prow_job_name}/{self.args.prow_run_name}/{self.args.prow_artifact_path}"
        logging.info(f"Downloading {from_url} to {self.args.prow_data_file}")
        response = requests.get(from_url)
        response.raise_for_status()

        with open(self.args.prow_data_file, "wb") as f:
            f.write(response.content)

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
            "--prow-run-name",
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

        logging.info("Searching if already present")

        query = {
            "query": {
                "match": {f"{self.args.matcher_field}": self.args.matcher_field_value}
            }
        }
        headers = {"Content-Type": "application/json"}

        current_doc_in_es = requests.post(
            f"{self.args.es_host_url}/{self.args.es_index}/_search",
            headers=headers,
            json=query,
        )
        current_doc_in_es.raise_for_status()
        current_doc_in_es = current_doc_in_es.json()

        if current_doc_in_es["hits"]["total"]["value"] > 0:
            print(
                f"Document with {self.args.matcher_field}={self.args.matcher_field_value} already present, skipping upload"
            )
            return

        logging.info("Uploading")

        with open(self.args.data_file, "r") as fp:
            values = json.load(fp)

        response = requests.post(
            f"{self.args.es_host_url}/{self.args.es_index}/_doc",
            headers=headers,
            json=values,
        )
        response.raise_for_status()
        print(f"Uploaded: {response.content}")

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
            default="rhtap_ci_status_data",
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

        # FIXME
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.logger.debug("Getting access token from Keycloak")
        response = requests.post(
            f"{self.args.horreum_keycloak_host}/realms/horreum/protocol/openid-connect/token",
            data={
                "username": self.args.horreum_keycloak_user,
                "password": self.args.horreum_keycloak_pass,
                "grant_type": "password",
                "client_id": "horreum-ui",
            },
            verify=False,
        )
        response.raise_for_status()

        self.token = response.json()["access_token"]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        self.logger.debug(f"Getting test id for {self.args.test_name_horreum}")
        response = requests.get(
            f"{self.args.horreum_host}/api/test/byName/{self.args.test_name_horreum}",
            headers=self.headers,
            verify=False,
        )
        response.raise_for_status()
        self.test_id = response.json()["id"]

    def upload(self):
        if self.args.horreum_data_file is None:
            raise Exception(
                "Horreum data file is required to work with --horreum-upload"
            )
        elif self.args.horreum_host is None:
            raise Exception("Horreum host is required to work with --horreum-upload")
        elif self.args.test_start is None:
            raise Exception("Test start is required to work with --horreum-upload")
        elif self.args.test_end is None:
            raise Exception("Test end is required to work with --horreum-upload")
        elif self.args.test_job_matcher_label is None:
            raise Exception("Test job matcher Horreum label name is required to work with --horreum-upload")

        self.logger.debug(f"Loading file {self.args.horreum_data_file}")
        with open(self.args.horreum_data_file, "r") as fd:
            values = json.load(fd)

        test_matcher = values[self.args.test_job_matcher]
        self.logger.debug(
            f"Searching if result with {self.args.test_job_matcher_label}={test_matcher} is already there"
        )
        filter_data = {self.args.test_job_matcher_label: test_matcher}
        response = requests.get(
            f"{self.args.horreum_host}/api/dataset/list/{self.test_id}",
            headers=self.headers,
            params={"filter": json.dumps(filter_data)},
            verify=False,
        )
        response.raise_for_status()
        datasets = response.json().get("datasets", [])
        if len(datasets) > 0:
            print(
                f"Result {self.args.test_job_matcher_label}={test_matcher} is already there, skipping upload"
            )
            return

        logging.info("Uploading")

        params = {
            "test": self.args.test_name_horreum,
            "start": self.args.test_start,
            "stop": self.args.test_end,
            "owner": self.args.test_owner,
            "access": self.args.test_access,
        }
        response = requests.post(
            f"{self.args.horreum_host}/api/run/data",
            params=params,
            headers=self.headers,
            data=json.dumps(values),
            verify=False,
        )
        response.raise_for_status()

        print(f"Uploaded {self.args.horreum_data_file}: {response.content}")

    def result(self):
        if self.args.horreum_data_file is None:
            raise Exception(
                "Horreum data file is required to work with --horreum-result"
            )
        elif self.args.test_start is None:
            raise Exception("Test start is required to work with --horreum-result")
        elif self.args.test_end is None:
            raise Exception("Test end is required to work with --horreum-result")

        sd = status_data.StatusData(self.args.horreum_data_file)
        if sd.get("result") is not None:
            print(
                f"Result field ({sd.get('result')}) already there in {self.args.horreum_data_file}, skipping changes detection"
            )
            return

        self.logger.debug(f"Loading list of alerting variables for test {self.test_id}")
        response = requests.get(
            f"{self.args.horreum_host}/api/alerting/variables",
            params={"test": self.test_id},
            verify=False,
        )
        response.raise_for_status()
        alerting_variables = response.json()

        change_detected = False
        for alerting_variable in alerting_variables:
            self.logger.debug(
                f"Getting changes for alerting variable {alerting_variable}"
            )

            range_data = {
                "range": {
                    "from": self.args.test_start,
                    "to": self.args.test_end,
                    "oneBeforeAndAfter": True,
                },
                "annotation": {"query": alerting_variable["id"]},
            }
            response = requests.post(
                f"{self.args.horreum_host}/api/changes/annotations",
                headers=self.headers,
                json=range_data,
                verify=False,
            )
            response.raise_for_status()
            response = response.json()

            # Check if the result is not an empty list
            if len(response) > 0:
                self.logger.debug(f"Detected change {response}")
                change_detected = True
                break

        print(f"Writing result to {self.args.horreum_data_file}: {'FAIL' if change_detected else 'PASS'}")
        if change_detected:
            sd.set("result", "FAIL")
        else:
            sd.set("result", "PASS")
        sd.save()

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
        group.add_argument("--horreum-keycloak-host", help="Horreum Keycloak host url")
        group.add_argument("--horreum-keycloak-user", help="Horreum Keycloak username")
        group.add_argument("--horreum-keycloak-pass", help="Horreum Keycloak password")
        group.add_argument(
            "--test-name-horreum", default="load-tests-result", help="Test Name"
        )
        group.add_argument("--test-job-matcher", default="jobName", help="Field name in JSON with unique enough value we use to detect if document is already in Horreum")
        group.add_argument("--test-job-matcher-label", help="Label name in Horreum with unique enough value we use to detect if document is already in Horreum")
        group.add_argument("--test-owner", default="rhtap-perf-test-team")
        group.add_argument("--test-access", default="PUBLIC")
        group.add_argument("--test-start", help="time when the test started")
        group.add_argument("--test-end", help="time when the test ended")


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

        # FIXME: Field names where to get these should come from params
        self.logger.debug(f"Loading data from {self.args.status_data}")
        with open(self.args.status_data, "r") as fd:
            values = json.load(fd)
        date = values["timestamp"]
        link = values["jobLink"]
        result = values["result"]
        result_id = values["metadata"]["env"]["BUILD_ID"]

        self.logger.debug(
            f"Checking if result with result_id={result_id} is already there"
        )
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
        current_doc_in_es.raise_for_status()
        current_doc_in_es = current_doc_in_es.json()

        if current_doc_in_es["hits"]["total"]["value"] > 0:
            print(
                f"Result result_id={result_id} already in Results Dashboard, skipping upload"
            )
            return

        logging.info("Uploading result to Results Dashboard")

        upload_data = {
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
        response = requests.post(
            f"{self.args.es_host_url}/{self.args.dashboard_es_index}/_doc",
            headers=headers,
            json=upload_data,
        )
        response.raise_for_status()

        print(f"Uploaded: {response.content}")

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
