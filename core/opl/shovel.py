#!/usr/bin/env python

import argparse
import datetime
import logging
import requests
import json
import os
import re
import urllib3

from opl import skelet, status_data


def _floor_datetime(obj):
    """Floor datetime object to whole second."""
    return obj.replace(microsecond=0)

def _ceil_datetime(obj):
    """Ceil datetime object to whole second."""
    if obj.microsecond > 0:
        obj += datetime.timedelta(seconds=1)
    return obj.replace(microsecond=0)

def _get_field_value(field, data):
    """Return content of filed like foo.bar or .baz or so."""
    value = None
    for f in field.split("."):
        if f == '':
            continue   # skip empty field created e.g. by leading dot
        if value is None:
            value = data[f]
        else:
            value = value[f]
    return value


class pluginBase:
    def __init__(self):
        self.logger = logging.getLogger(str(self.__class__))

    def set_args(parser, subparsers):
        pass


class pluginProw(pluginBase):
    def list(self, args):
        response = requests.get(f"{args.base_url}/{args.job_name}")
        response.raise_for_status()

        # Extract 19-digit numbers using regular expression
        numbers = re.findall(r"\b[0-9]{19}\b", response.text)

        # Sort the numbers in numerical order and get the last 10 unique numbers
        sorted_numbers = sorted(set(numbers), key=lambda x: int(x))
        last_10_numbers = sorted_numbers[-10:]
        for n in last_10_numbers:
            print(n)

    def download(self, args):
        if os.path.isfile(args.output_path):
            raise Exception(f"File {args.output_path} already present, refusing to overwrite it")

        from_url = f"{args.base_url}/{args.job_name}/{args.job_run_id}/artifacts/{args.run_name}/{args.artifact_path}"
        logging.info(f"Downloading {from_url} to {args.output_path}")
        response = requests.get(from_url)
        response.raise_for_status()

        with open(args.output_path, "wb") as f:
            f.write(response.content)

    def set_args(self, parser, subparsers):
        # Generic Prow options
        parser.add_argument(
            "--base-url",
            default="https://gcsweb-ci.apps.ci.l2s4.p1.openshiftapps.com/gcs/test-platform-results/logs/",
            help="Base URL of Prow exporter",
        )
        parser.add_argument(
            "--job-name",
            default="periodic-ci-konflux-ci-e2e-tests-main-load-test-ci-daily-100u",
            help="Job name as available in ci-operator/jobs/...",
        )

        # Options for listing Prow runs
        parser_list = subparsers.add_parser("list", help="List runs for specific Prow job")
        parser_list.set_defaults(func=self.list)

        # Options for downloading artifacts from Prow
        parser_download = subparsers.add_parser("download", help="Download file from Prow run artifacts")
        parser_download.set_defaults(func=self.download)
        parser_download.add_argument(
            "--job-run-id",
            required=True,
            help="Long run number identifier",
        )
        parser_download.add_argument(
            "--run-name",
            default="load-test-ci-daily-100u",
            help="Test name as configured in ci-operator/config/...",
        )
        parser_download.add_argument(
            "--artifact-path",
            default="redhat-appstudio-load-test/artifacts/load-test.json",
            help="Path to the artifact in artifacts/ directory",
        )
        parser_download.add_argument(
            "--output-path",
            required=True,
            help="Filename where to put downloaded artifact",
        )


class pluginOpenSearch(pluginBase):
    def upload(self, args):
        self.logger.info(f"Loading document {args.input_file}")
        with open(args.input_file, "r") as fp:
            values = json.load(fp)

        if args.matcher_field.startswith("."):
            args.matcher_field = args.matcher_field[1:]
        self.logger.info(f"Looking for field {args.matcher_field}")
        matcher_value = _get_field_value(args.matcher_field, values)
        if matcher_value is None:
            raise Exception(f"Failed to load {args.matcher_field} from {args.input_file}")

        self.logger.info(f"Checking if document {args.matcher_field}={matcher_value} is already present")
        query = {
            "query": {
                "match": {f"{args.matcher_field}": matcher_value}
            }
        }
        headers = {"Content-Type": "application/json"}

        current_doc_in_es = requests.post(
            f"{args.base_url}/{args.index}/_search",
            headers=headers,
            json=query,
        )
        current_doc_in_es.raise_for_status()
        current_doc_in_es = current_doc_in_es.json()

        if current_doc_in_es["hits"]["total"]["value"] > 0:
            print(
                f"Document {args.matcher_field}={matcher_value} is already present, skipping upload"
            )
            return

        self.logger.info("Uploading document")
        response = requests.post(
            f"{args.base_url}/{args.index}/_doc",
            headers=headers,
            json=values,
        )
        response.raise_for_status()
        print(f"Uploaded: {response.content}")

    def set_args(self, parser, subparsers):
        parser.add_argument(
            "--base-url",
            default="http://elasticsearch.intlab.perf-infra.lab.eng.rdu2.redhat.com",
            help="Base URL of OpenSearch server",
        )
        parser.add_argument(
            "--index",
            default="rhtap_ci_status_data",
            help="Index to talk to",
        )

        # Options for uploading document to OpenSearch
        parser_upload = subparsers.add_parser("upload", help="Upload document to OpenSearch")
        parser_upload.set_defaults(func=self.upload)
        parser_upload.add_argument(
            "--input-file",
            required=True,
            help="JSON file to upload",
        )
        parser_upload.add_argument(
            "--matcher-field",
            help="Document field which holds unique value identifying the document. Will be used for checking if data exists on the server, value will be taken from input file.",
        )


class pluginHorreum(pluginBase):
    def _login(self, args):
        # FIXME
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.logger.debug("Getting access token from Keycloak")
        response = requests.post(
            f"{args.keycloak_url}/realms/horreum/protocol/openid-connect/token",
            data={
                "username": args.username,
                "password": args.password,
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

        self.logger.debug(f"Getting test id for {args.test_name}")
        response = requests.get(
            f"{args.base_url}/api/test/byName/{args.test_name}",
            headers=self.headers,
            verify=False,
        )
        response.raise_for_status()
        self.test_id = response.json()["id"]

    def upload(self, args):
        self._login(args)

        self.logger.debug(f"Loading file {args.input_file}")
        with open(args.input_file, "r") as fd:
            values = json.load(fd)

        if args.matcher_field.startswith("."):
            args.matcher_field = args.matcher_field[1:]
        self.logger.info(f"Looking for field {args.matcher_field}")
        matcher_value = _get_field_value(args.matcher_field, values)
        if matcher_value is None:
            raise Exception(f"Failed to load {args.matcher_field} from {args.input_file}")

        self.logger.debug(
            f"Searching if result with {args.matcher_label}={matcher_value} is already there"
        )
        filter_data = {args.matcher_label: matcher_value}
        response = requests.get(
            f"{args.base_url}/api/dataset/list/{self.test_id}",
            headers=self.headers,
            params={"filter": json.dumps(filter_data)},
            verify=False,
        )
        response.raise_for_status()
        datasets = response.json().get("datasets", [])
        if len(datasets) > 0:
            print(
                f"Result {args.matcher_label}={matcher_value} is already there, skipping upload"
            )
            return

        logging.info("Uploading")
        params = {
            "test": args.test_name_horreum,
            "start": args.test_start,
            "stop": args.test_end,
            "owner": args.test_owner,
            "access": args.test_access,
        }
        response = requests.post(
            f"{args.horreum_host}/api/run/data",
            params=params,
            headers=self.headers,
            data=json.dumps(values),
            verify=False,
        )
        response.raise_for_status()

        print(f"Uploaded {args.horreum_data_file}: {response.content}")

    def result(self, args):
        self._login(args)

        self.logger.debug(f"Loading list of alerting variables for test {self.test_id}")
        response = requests.get(
            f"{args.base_url}/api/alerting/variables",
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

            start = _floor_datetime(args.start.astimezone(tz=datetime.timezone.utc))
            end = _ceil_datetime(args.end.astimezone(tz=datetime.timezone.utc))
            start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")

            range_data = {
                "range": {
                    "from": start_str,
                    "to": end_str,
                    "oneBeforeAndAfter": True,
                },
                "annotation": {"query": alerting_variable["id"]},
            }
            response = requests.post(
                f"{args.base_url}/api/changes/annotations",
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

        result = 'FAIL' if change_detected else 'PASS'

        if args.output_file is None:
            print(f"Result is {result}")
            return

        self.logger.debug(f"Loading file {args.output_file}")
        with open(args.output_file, "r") as fd:
            values = json.load(fd)

        values["result"] = result

        print(f"Writing result to {args.output_file}: {values['result']}")
        with open(args.output_file, "w") as fd:
            json.dump(values, fd, sort_keys=True, indent=4)

    def set_args(self, parser, subparsers):
        parser.add_argument(
            "--base-url",
            default="https://horreum.corp.redhat.com",
            help="Base URL of Horreum server",
        )
        parser.add_argument(
            "--keycloak-url",
            default="https://horreum-keycloak.corp.redhat.com",
            help="Base URL of Horreum Keycloak server",
        )
        parser.add_argument(
            "--username",
            required=True,
            help="Horreum username",
        )
        parser.add_argument(
            "--password",
            required=True,
            help="Horreum password",
        )
        parser.add_argument(
            "--test-name",
            default="load-tests-result",
            help="Test Name",
        )

        # Options for uploading document to Horreum
        parser_upload = subparsers.add_parser("upload", help="Upload file to Horreum if it is not there already")
        parser_upload.set_defaults(func=self.upload)
        parser_upload.add_argument(
            "--input-file",
            required=True,
            help="JSON file to upload",
        )
        parser_upload.add_argument(
            "--matcher-field",
            default="runid",
            help="JSON file field which holds unique value identifying the document. Will be used for checking if data exists on the server, value will be taken from input file.",
        )
        parser_upload.add_argument(
            "--matcher-label",
            default=".runid",
            help="Label name in Horreum with unique value we use to detect if document is already in Horreum",
        )
        parser_upload.add_argument(
            "--owner",
            default="rhtap-perf-test-team",
            help="Who should be owner of uploaded file in Horreum",
        )
        parser_upload.add_argument(
            "--access",
            default="PUBLIC",
            help="What should be access setting of uploaded file in Horreum",
        )
        parser_upload.add_argument(
            "--start",
            help="When the test whose JSON file we are uploading started",
        )
        parser_upload.add_argument(
            "--end",
            help="When the test whose JSON file we are uploading ended",
        )

        # Options for detecting no-/change signal
        parser_result = subparsers.add_parser("result", help="Get Horreum no-/change signal for a given time range")
        parser_result.set_defaults(func=self.result)
        parser_result.add_argument(
            "--start",
            type=datetime.datetime.fromisoformat,
            help="Start of the interval for detecting change (ISO 8601 format)",
        )
        parser_result.add_argument(
            "--end",
            type=datetime.datetime.fromisoformat,
            help="End of the interval for detecting change (ISO 8601 format)",
        )
        parser_result.add_argument(
            "--output-file",
            help="If specified, put result into .result of this JSON file",
        )


class pluginResultsDashboard(pluginBase):
    def _figure_out_option(self, option):
        if option.startswith("@"):
            field = option[1:]
            value = _get_field_value(field, self.input_file)
            if value is None:
                raise Exception(f"Can not load {field}")
            else:
                return value
        else:
            if option is None:
                raise Exception("Some option was not provided")
            else:
                return option

    def upload(self, args):
        self.input_file = None
        if args.input_file is not None:
            self.logger.info(f"Loading input file {args.input_file}")
            with open(args.input_file, "r") as fd:
                self.input_file = json.load(fd)

        self.logger.info("Preparing all the options")
        args.date = datetime.datetime.fromisoformat(self._figure_out_option(args.date))
        args.group = self._figure_out_option(args.group)
        args.link = self._figure_out_option(args.link)
        args.product = self._figure_out_option(args.product)
        args.release = self._figure_out_option(args.release)
        args.result = self._figure_out_option(args.result)
        args.result_id = self._figure_out_option(args.result_id)
        args.test = self._figure_out_option(args.test)
        args.version = self._figure_out_option(args.version)

        self.logger.info(
            f"Checking if result with test={args.test} and result_id={args.result_id} is already there"
        )
        json_data = json.dumps(
            {
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"test.keyword": args.test}},
                            {"term": {"result_id.keyword": args.result_id}},
                        ]
                    }
                }
            }
        )
        headers = {"Content-Type": "application/json"}
        current_doc_in_es = requests.get(
            f"{args.base_url}/{args.index}/_search",
            headers=headers,
            data=json_data,
        )
        current_doc_in_es.raise_for_status()
        current_doc_in_es = current_doc_in_es.json()

        if current_doc_in_es["hits"]["total"]["value"] > 0:
            print(
                f"Result test={args.test} and result_id={args.result_id} already in Results Dashboard, skipping upload"
            )
            return

        logging.info("Uploading result to Results Dashboard")

        upload_data = {
            "date": args.date.isoformat(),
            "group": args.group,
            "link": args.link,
            "product": args.product,
            "release": args.release,
            "result": args.result,
            "result_id": args.result_id,
            "test": args.test,
            "version": args.version,
        }
        response = requests.post(
            f"{args.base_url}/{args.index}/_doc",
            headers=headers,
            json=upload_data,
        )
        response.raise_for_status()

        print(f"Uploaded: {response.content}")

    def set_args(self, parser, subparsers):
        parser.add_argument(
            "--base-url",
            default="http://elasticsearch.intlab.perf-infra.lab.eng.rdu2.redhat.com",
            help="Results Dashboard backend url",
        )
        parser.add_argument(
            "--index",
            default="results-dashboard-data",
            help="Results Dashboard index where the results are stored",
        )

        # Options for uploading document to Results Dashboard
        parser_upload = subparsers.add_parser("upload", help="Upload result to Results Dashboard if it is not there already")
        parser_upload.set_defaults(func=self.upload)
        parser_upload.add_argument(
            "--test",
            required=True,
            help="Name of the CPT test, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--result-id",
            required=True,
            help="Test run identifier, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--result",
            required=True,
            help="Result of the test (choose from: TODO), if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--date",
            required=True,
            help="When the test ran (ISO 8601 format), if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--link",
            required=True,
            help="Link to more details, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--group",
            required=True,
            help="Name of the group where the product belongs, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--product",
            required=True,
            help="Name of the product, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--release",
            default="latest",
            help="Release or version stream this result belongst to (this is a way how to group results for multiple versions), if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--version",
            default="1",
            help="Version of the product on which the test ran, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        parser_upload.add_argument(
            "--input-file",
            help="If you want to load some values from file, this is the file to specify",
        )


PLUGINS = {
    "prow": pluginProw(),
    "opensearch": pluginOpenSearch(),
    "horreum": pluginHorreum(),
    "resultsdashboard": pluginResultsDashboard(),
}

def main():
    parser = argparse.ArgumentParser(
        description="Shovel data from A to B",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest='plugin_name',
        help="sub-command help",
        required=True,
    )
    for name, plugin in PLUGINS.items():
        parser_plugin = subparsers.add_parser(
            name,
            help=f"Work with {name}",
        )
        subparsers_plugin = parser_plugin.add_subparsers(
            dest='plugin_command',
            help="sub-command help",
            required=True,
        )
        plugin.set_args(parser_plugin, subparsers_plugin)

    with skelet.test_setup(parser) as (args, status_data):
        args.func(args)

if __name__ == "__main__":
    main()
