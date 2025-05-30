#!/usr/bin/env python

import argparse
import datetime
import logging
import requests
import json
import os
import re
import urllib3
import urllib.parse

from opl import skelet


def _check_response(logger, response):
    """Check if requests response is OKish and if not, log useful data and raise exception."""
    try:
        response.raise_for_status()
    except Exception:
        logger.error(f"Request failed with text: {response.text}")
        raise


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
    if field.startswith("."):
        field = field[1:]

    value = None
    for f in field.split("."):
        if f == "":
            continue  # skip empty field created e.g. by leading dot
        if value is None:
            value = data[f]
        else:
            value = value[f]

    return value


def _set_field_value(field, value, data):
    """Find field (in doted notation) in data (being changed in place) and set it to value."""
    if field.startswith("@"):
        field = field[1:]

    for f in field.split(".")[:-1]:
        if f not in data:
            data[f] = {}
        data = data[f]

    data[field.split(".")[-1]] = value


def _figure_out_option(option, data):
    """Normalize option value for cases when it can come from data file. Checks for None."""
    if option.startswith("@"):
        field = option[1:]
        value = _get_field_value(field, data)
        if value is None:
            raise Exception(f"Can not load {field} in {option}")
        else:
            return value
    else:
        if option is None:
            raise Exception("Some option was not provided")
        else:
            return option


class pluginBase:
    def __init__(self):
        self.logger = logging.getLogger(str(self.__class__))

    def set_args(parser, subparsers):
        pass


class pluginProw(pluginBase):
    def list(self, args):
        response = requests.get(f"{args.base_url}/{args.job_name}")
        _check_response(self.logger, response)

        # Extract 19-digit numbers using regular expression
        numbers = re.findall(r"\b[0-9]{19}\b", response.text)

        # Sort the numbers in numerical order and get the last 10 unique numbers
        sorted_numbers = sorted(set(numbers), key=lambda x: int(x))
        last_10_numbers = sorted_numbers[-10:]
        for n in last_10_numbers:
            print(n)

    def download(self, args):
        if os.path.isfile(args.output_path):
            raise Exception(
                f"File {args.output_path} already present, refusing to overwrite it"
            )

        from_url = f"{args.base_url}/{args.job_name}/{args.job_run_id}/artifacts/{args.run_name}/{args.artifact_path}"
        logging.info(f"Downloading {from_url} to {args.output_path}")
        response = requests.get(from_url)
        _check_response(self.logger, response)
        response_content = response.content

        if args.record_link is not None:
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                self.logger.error(
                    "Failed to parse JSON, ignoring --record-link option"
                )
            else:
                _set_field_value(args.record_link, from_url, data)
                response_content = str.encode(
                    json.dumps(data, sort_keys=True, indent=4)
                )

        with open(args.output_path, "wb") as f:
            f.write(response_content)

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
        parser_list = subparsers.add_parser(
            "list", help="List runs for specific Prow job"
        )
        parser_list.set_defaults(func=self.list)

        # Options for downloading artifacts from Prow
        parser_download = subparsers.add_parser(
            "download", help="Download file from Prow run artifacts"
        )
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
        parser_download.add_argument(
            "--record-link",
            help="Optional path in the downloaded JSON where to put download link",
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
            raise Exception(
                f"Failed to load {args.matcher_field} from {args.input_file}"
            )

        self.logger.info(
            f"Checking if document {args.matcher_field}={matcher_value} is already present"
        )
        query = {"query": {"match": {f"{args.matcher_field}": matcher_value}}}
        headers = {"Content-Type": "application/json"}

        current_doc_in_es = requests.post(
            f"{args.base_url}/{args.index}/_search",
            headers=headers,
            json=query,
        )
        _check_response(self.logger, current_doc_in_es)
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
        _check_response(self.logger, response)
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
        parser_upload = subparsers.add_parser(
            "upload", help="Upload document to OpenSearch"
        )
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
    def _setup(self, args):
        # FIXME
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.headers = {
            "Content-Type": "application/json",
            "X-Horreum-API-Key": args.api_token,
        }

        if "test_name" in args:
            self.logger.debug(f"Getting test id for {args.test_name}")
            response = requests.get(
                f"{args.base_url}/api/test/byName/{args.test_name}",
                headers=self.headers,
                verify=False,
            )
            _check_response(self.logger, response)
            self.test_id = response.json()["id"]

    def upload(self, args):
        self.logger.debug(f"Loading file {args.input_file}")
        with open(args.input_file, "r") as fd:
            self.input_file = json.load(fd)

        self.logger.info("Preparing all the options")
        args.test_name = _figure_out_option(args.test_name, self.input_file)
        args.start = datetime.datetime.fromisoformat(
            _figure_out_option(args.start, self.input_file)
        )
        args.end = datetime.datetime.fromisoformat(
            _figure_out_option(args.end, self.input_file)
        )

        self._setup(args)

        self.logger.info(f"Looking for field {args.matcher_field}")
        matcher_value = _get_field_value(args.matcher_field, self.input_file)
        if matcher_value is None:
            raise Exception(
                f"Failed to load {args.matcher_field} from {args.input_file}"
            )

        self.logger.debug(
            f"Searching if result {args.matcher_label}={matcher_value} is already there"
        )
        filter_data = {args.matcher_label: matcher_value}
        response = requests.get(
            f"{args.base_url}/api/dataset/list/{self.test_id}",
            headers=self.headers,
            params={"filter": json.dumps(filter_data)},
            verify=False,
        )
        _check_response(self.logger, response)
        datasets = response.json().get("datasets", [])
        if len(datasets) > 0:
            print(
                f"Result {args.matcher_label}={matcher_value} is already there, skipping upload"
            )
            return

        if args.trashed:
            self.logger.debug(
                "WORKAROUND: Searching if result already there amongst trashed runs"
            )
            params = {
                "trashed": True,
                "limit": args.trashed_workaround_count,
                "page": 1,
                "sort": "start",
                "direction": "Descending",
            }
            response = requests.get(
                f"{args.base_url}/api/run/list/{self.test_id}",
                headers=self.headers,
                params=params,
                verify=False,
            )
            _check_response(self.logger, response)
            runs = response.json().get("runs", [])

            for run in runs:
                # Un-trashed runs were examined already, so we can skipp these
                if run["trashed"] is False:
                    continue

                response = requests.get(
                    f"{args.base_url}/api/run/{run['id']}/data",
                    headers=self.headers,
                    verify=False,
                )
                _check_response(self.logger, response)
                run_data = response.json()
                try:
                    marker = _get_field_value(args.matcher_field, run_data)
                except KeyError:
                    pass   # If matcher was not found in data, we can assume this is not a duplicate
                else:
                    if marker == matcher_value:
                        print(
                            f"Result {args.matcher_field}={matcher_value} is trashed, but already there, skipping upload"
                        )
                        return

        logging.info("Uploading")
        params = {
            "test": args.test_name,
            "start": args.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stop": args.end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "owner": args.owner,
            "access": args.access,
        }
        response = requests.post(
            f"{args.base_url}/api/run/data",
            params=params,
            headers=self.headers,
            data=json.dumps(self.input_file),
            verify=False,
        )
        _check_response(self.logger, response)

        print(f"Uploaded {args.input_file}: {response.content}")

    def result(self, args):
        self.logger.debug(f"Loading file {args.output_file}")
        with open(args.output_file, "r") as fd:
            self.output_file = json.load(fd)

        self.logger.info("Preparing all the options")
        args.test_name = _figure_out_option(args.test_name, self.output_file)
        args.start = datetime.datetime.fromisoformat(
            _figure_out_option(args.start, self.output_file)
        ).astimezone(tz=datetime.timezone.utc)
        args.end = datetime.datetime.fromisoformat(
            _figure_out_option(args.end, self.output_file)
        ).astimezone(tz=datetime.timezone.utc)

        self._setup(args)

        self.logger.debug(f"Loading list of alerting variables for test {self.test_id}")
        response = requests.get(
            f"{args.base_url}/api/alerting/variables",
            params={"test": self.test_id},
            verify=False,
        )
        _check_response(self.logger, response)
        alerting_variables = response.json()

        start = _floor_datetime(args.start)
        end = _ceil_datetime(args.end)
        start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")

        change_detected = False
        for alerting_variable in alerting_variables:
            self.logger.debug(
                f"Getting changes for alerting variable {alerting_variable}"
            )

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
            _check_response(self.logger, response)
            response = response.json()

            # Check if the result is not an empty list
            if len(response) > 0:
                self.logger.info(
                    f"For {alerting_variable['name']} detected change {response}"
                )
                change_detected = True
                break
            else:
                self.logger.info(f"For {alerting_variable['name']} all looks good")

        result = "FAIL" if change_detected else "PASS"

        if args.output_file is None:
            print(f"Result is {result}")
            return

        self.output_file["result"] = result

        print(f"Writing result to {args.output_file}: {self.output_file['result']}")
        with open(args.output_file, "w") as fd:
            json.dump(self.output_file, fd, sort_keys=True, indent=4)

    def list(self, args):
        self._setup(args)

        params = {
            "trashed": False,
            "limit": 100,
            "page": 1,
        }

        self.logger.debug(f"Listing results for test {args.test_name}")
        while True:
            response = requests.get(
                f"{args.base_url}/api/run/list/{self.test_id}",
                headers=self.headers,
                params=params,
                verify=False,
            )
            _check_response(self.logger, response)

            runs = response.json().get("runs", [])
            if len(runs) == 0:
                break

            for i in runs:
                print(i["id"])

            params["page"] += 1

    def get(self, args):
        self._setup(args)

        self.logger.debug(f"Geting data for run {args.run_id}")
        response = requests.get(
            f"{args.base_url}/api/run/{args.run_id}/data",
            headers=self.headers,
            verify=False,
        )
        _check_response(self.logger, response)
        data = response.json()
        print(json.dumps(data))

    def _schema_uri_to_id(self, base_url, schema_uri):
        self.logger.debug(f"Geting schema ID for URI {schema_uri}")
        response = requests.get(
            f"{base_url}/api/schema/idByUri/{schema_uri}",
            headers=self.headers,
            verify=False,
        )
        _check_response(self.logger, response)
        schema_id = int(response.json())
        self.logger.debug(f"Schema ID for URI {schema_uri} is {schema_id}")
        return schema_id

    def _sanitize_string(self, input_string):
        return re.sub(r"[^a-zA-Z0-9]", "_", input_string)

    def _schema_id_labels(self, args, schema_id):
        self.logger.debug(f"Getting list of labels for schema ID {schema_id}")
        response = requests.get(
            f"{args.base_url}/api/schema/{schema_id}/labels",
            headers=self.headers,
            verify=False,
        )
        _check_response(self.logger, response)
        data = response.json()
        self.logger.debug(f"Obtained {len(data)} labels for schema ID {schema_id}")

        return data

    def schema_label_list(self, args):
        self._setup(args)

        schema_id = self._schema_uri_to_id(args.base_url, args.schema_uri)

        labels = self._schema_id_labels(args, schema_id)

        for label in labels:
            print(f"{label['id']}\t{label['name']}\t{label['extractors'][0]['jsonpath']}")

    def schema_label_add(self, args):
        self._setup(args)

        schema_id = self._schema_uri_to_id(args.base_url, args.schema_uri)

        new_name = (
            self._sanitize_string(args.extractor_jsonpath)
            if args.name is None
            else args.name
        )
        new_ext_name = (
            self._sanitize_string(args.extractor_jsonpath)
            if args.extractor_name is None
            else args.extractor_name
        )
        new = {
            "access": args.access,
            "owner": args.owner,
            "name": new_name,
            "extractors": [
                {
                    "name": new_ext_name,
                    "jsonpath": args.extractor_jsonpath,
                    "isarray": args.extractor_isarray,
                },
            ],
            "function": args.function,
            "filtering": args.filtering,
            "metrics": args.metrics,
            "schemaId": schema_id,
        }

        self.logger.debug(f"Adding label to schema id {schema_id}: {new}")
        response = requests.post(
            f"{args.base_url}/api/schema/{schema_id}/labels",
            headers=self.headers,
            verify=False,
            json=new,
        )
        _check_response(self.logger, response)
        label_id = int(response.json())
        self.logger.debug(f"Created label ID {label_id} in schema ID {schema_id}")

    def schema_label_update(self, args):
        self._setup(args)

        schema_id = self._schema_uri_to_id(args.base_url, args.schema_uri)

        new_name = (
            self._sanitize_string(args.extractor_jsonpath)
            if args.name is None
            else args.name
        )
        new_ext_name = (
            self._sanitize_string(args.extractor_jsonpath)
            if args.extractor_name is None
            else args.extractor_name
        )
        new = {
            "access": args.access,
            "owner": args.owner,
            "name": new_name,
            "extractors": [
                {
                    "name": new_ext_name,
                    "jsonpath": args.extractor_jsonpath,
                    "isarray": args.extractor_isarray,
                },
            ],
            "function": args.function,
            "filtering": args.filtering,
            "metrics": args.metrics,
            "schemaId": schema_id,
        }

        # Account options that allow updating existing label
        if args.update_by_id is not None or args.update_by_name is not None:
            labels = self._schema_id_labels(args, schema_id)

        if args.update_by_id is not None:
            label = next((item for item in labels if item["id"] == args.update_by_id), False)

            if label:
                # Label with provided id found, lets update it
                new["id"] = args.update_by_id
            else:
                # Label not found
                raise KeyError(f"Failed to find label with id {args.update_by_id}")

        elif args.update_by_name is not None:
            label = next((item for item in labels if item["name"] == new_name), False)

            if label:
                # Label with provided name found, lets update it
                new["id"] = label["id"]
            else:
                # Label not found, shall we fail now?
                if args.add_if_missing:
                    self.logger.warning(f"Label with name {new_name} not found, so adding new one with new ID")
                    return self.schema_label_add(args)
                else:
                    raise KeyError(f"Failed to find label with name {new_name}")
        else:
            raise Exception("Either --update-by-id or --update-by-name have to be used")

        if new == label:
            self.logger.info(f"Proposed and current label {label['id']} in schema ID {schema_id} are same, nothing to change")
        else:
            self.logger.debug(f"Updating label in schema id {schema_id}: {new}")
            response = requests.put(
                f"{args.base_url}/api/schema/{schema_id}/labels",
                headers=self.headers,
                verify=False,
                json=new,
            )
            _check_response(self.logger, response)
            label_id = int(response.json())
            self.logger.info(f"Updated label ID {label_id} in schema ID {schema_id}")

    def schema_label_delete(self, args):
        self._setup(args)

        schema_id = self._schema_uri_to_id(args.base_url, args.schema_uri)

        self.logger.debug(f"Deleting label ID {args.id} from schema ID {schema_id}")
        response = requests.delete(
            f"{args.base_url}/api/schema/{schema_id}/labels/{args.id}",
            headers=self.headers,
            verify=False,
        )
        _check_response(self.logger, response)
        self.logger.debug(f"Deleted label ID {args.id} in schema ID {schema_id}")

    def set_args(self, parser, subparsers):
        parser.add_argument(
            "--base-url",
            default="https://horreum.corp.redhat.com",
            help="Base URL of Horreum server",
        )
        parser.add_argument(
            "--api-token",
            required=True,
            help="Horreum API token",
        )

        # Options for uploading document to Horreum
        subparser = subparsers.add_parser(
            "upload", help="Upload file to Horreum if it is not there already"
        )
        subparser.set_defaults(func=self.upload)
        subparser.add_argument(
            "--test-name",
            default="load-tests-result",
            help="Test name as configured in Horreum, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        subparser.add_argument(
            "--input-file",
            required=True,
            help="JSON file to upload",
        )
        subparser.add_argument(
            "--matcher-field",
            default="runid",
            help="JSON file field which holds unique value identifying the document. Will be used for checking if data exists on the server, value will be taken from input file.",
        )
        subparser.add_argument(
            "--matcher-label",
            default=".runid",
            help="Label name in Horreum with unique value we use to detect if document is already in Horreum",
        )
        subparser.add_argument(
            "--owner",
            default="rhtap-perf-test-team",
            help="Who should be owner of uploaded file in Horreum",
        )
        subparser.add_argument(
            "--access",
            default="PUBLIC",
            help="What should be access setting of uploaded file in Horreum",
        )
        subparser.add_argument(
            "--start",
            help="When the test whose JSON file we are uploading started, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        subparser.add_argument(
            "--end",
            help="When the test whose JSON file we are uploading ended, if prefixed with '@' sign, it is a field name from input file where to load this",
        )
        subparser.add_argument(
            "--trashed",
            action="store_true",
            help="Use this if you want to check for presence of a result even amongst trashed runs",
        )
        subparser.add_argument(
            "--trashed-workaround-count",
            default=10,
            help="When listing runs (including trashed ones) sorted in descending order, only check this many",
        )

        # Options for detecting no-/change signal
        subparser = subparsers.add_parser(
            "result", help="Get Horreum no-/change signal for a given time range"
        )
        subparser.set_defaults(func=self.result)
        subparser.add_argument(
            "--test-name",
            default="load-tests-result",
            help="Test name as configured in Horreum, if prefixed with '@' sign, it is a field name from output file where to load this",
        )
        subparser.add_argument(
            "--start",
            help="Start of the interval for detecting change (ISO 8601 format)",
        )
        subparser.add_argument(
            "--end",
            help="End of the interval for detecting change (ISO 8601 format)",
        )
        subparser.add_argument(
            "--output-file",
            help="If specified, put result into .result of this JSON file",
        )

        # Options for listing results
        subparser = subparsers.add_parser(
            "list", help="List test run IDs for a test"
        )
        subparser.set_defaults(func=self.list)
        subparser.add_argument(
            "--test-name",
            default="load-tests-result",
            help="Test name as configured in Horreum",
        )

        # Options for getting full result
        subparser = subparsers.add_parser("get", help="Get data for test run ID")
        subparser.set_defaults(func=self.get)
        subparser.add_argument(
            "--run-id",
            type=int,
            required=True,
            help="Test run ID",
        )

        # Options for listing schema labels
        subparser = subparsers.add_parser(
            "schema-label-list", help="List schema labels"
        )
        subparser.set_defaults(func=self.schema_label_list)
        subparser.add_argument(
            "--schema-uri",
            type=str,
            required=True,
            help="Schema URI identifier (e.g. 'uri:my-schema:0.1')",
        )

        # Options for adding schema label
        subparser = subparsers.add_parser(
            "schema-label-add", help="Add schema label"
        )
        subparser.set_defaults(func=self.schema_label_add)
        subparser.add_argument(
            "--schema-uri",
            type=str,
            required=True,
            help="Schema URI identifier (e.g. 'uri:my-schema:0.1')",
        )
        subparser.add_argument(
            "--name",
            type=str,
            help="Label name. Keep empty and it will de derived from JSON path.",
        )
        subparser.add_argument(
            "--extractor-name",
            type=str,
            help="Extractor name. Keep empty and it will de derived from JSON path. Only one extractor allowed now, support for more is TODO.",
        )
        subparser.add_argument(
            "--extractor-jsonpath",
            type=str,
            required=True,
            help="Extractor JSON path expression. Only one extractor allowed now, support for more is TODO.",
        )
        subparser.add_argument(
            "--extractor-isarray",
            type=bool,
            default=False,
            help="If extractor refferencing an array? Defaults to false. Only one extractor allowed now, support for more is TODO.",
        )
        subparser.add_argument(
            "--function",
            type=str,
            default="",
            help="Combination function for the label. Defaults to empty one.",
        )
        subparser.add_argument(
            "--filtering",
            action="store_true",
            help="Is label a filtering label? Defaults to false.",
        )
        subparser.add_argument(
            "--metrics",
            action="store_true",
            help="Is label a metrics label? Defaults to false.",
        )
        subparser.add_argument(
            "--access",
            choices=["PUBLIC", "PROTECTED", "PRIVATE"],
            default="PUBLIC",
            help="Access rights for the test. Defaults to 'PUBLIC'.",
        )
        subparser.add_argument(
            "--owner",
            type=str,
            required=True,
            help="Name of the team that owns the test.",
        )

        # Options for updating schema label
        subparser = subparsers.add_parser(
            "schema-label-update", help="Update schema label"
        )
        subparser.set_defaults(func=self.schema_label_update)
        subparser.add_argument(
            "--schema-uri",
            type=str,
            required=True,
            help="Schema URI identifier (e.g. 'uri:my-schema:0.1')",
        )
        subparser.add_argument(
            "--update-by-id",
            type=int,
            help="Label ID of label you want to update. Only set if you want to update existing label.",
        )
        subparser.add_argument(
            "--update-by-name",
            action="store_true",
            help="Label name of label you want to update. Only set if you want to update existing label.",
        )
        subparser.add_argument(
            "--add-if-missing",
            action="store_true",
            help="If updating (e.g. by name) and the target label is missing, attempt to create it.",
        )
        subparser.add_argument(
            "--name",
            type=str,
            help="Label name. Keep empty and it will de derived from JSON path.",
        )
        subparser.add_argument(
            "--extractor-name",
            type=str,
            help="Extractor name. Keep empty and it will de derived from JSON path. Only one extractor allowed now, support for more is TODO.",
        )
        subparser.add_argument(
            "--extractor-jsonpath",
            type=str,
            required=True,
            help="Extractor JSON path expression. Only one extractor allowed now, support for more is TODO.",
        )
        subparser.add_argument(
            "--extractor-isarray",
            type=bool,
            default=False,
            help="If extractor refferencing an array? Defaults to false. Only one extractor allowed now, support for more is TODO.",
        )
        subparser.add_argument(
            "--function",
            type=str,
            default="",
            help="Combination function for the label. Defaults to empty one.",
        )
        subparser.add_argument(
            "--filtering",
            action="store_true",
            help="Is label a filtering label? Defaults to false.",
        )
        subparser.add_argument(
            "--metrics",
            action="store_true",
            help="Is label a metrics label? Defaults to false.",
        )
        subparser.add_argument(
            "--access",
            choices=["PUBLIC", "PROTECTED", "PRIVATE"],
            default="PUBLIC",
            help="Access rights for the test. Defaults to 'PUBLIC'.",
        )
        subparser.add_argument(
            "--owner",
            type=str,
            required=True,
            help="Name of the team that owns the test.",
        )

        # Options for deleting schema label
        subparser = subparsers.add_parser(
            "schema-label-delete", help="Delete schema label"
        )
        subparser.set_defaults(func=self.schema_label_delete)
        subparser.add_argument(
            "--schema-uri",
            type=str,
            required=True,
            help="Schema URI identifier (e.g. 'uri:my-schema:0.1')",
        )
        subparser.add_argument(
            "--id",
            type=int,
            required=True,
            help="Label ID of label you want to delete",
        )


class pluginResultsDashboard(pluginBase):
    def upload(self, args):
        self.input_file = None
        if args.input_file is not None:
            self.logger.info(f"Loading input file {args.input_file}")
            with open(args.input_file, "r") as fd:
                self.input_file = json.load(fd)

        self.logger.info("Preparing all the options")
        args.date = datetime.datetime.fromisoformat(
            _figure_out_option(args.date, self.input_file)
        )
        args.group = _figure_out_option(args.group, self.input_file)
        args.link = _figure_out_option(args.link, self.input_file)
        args.product = _figure_out_option(args.product, self.input_file)
        args.release = _figure_out_option(args.release, self.input_file)
        args.result = _figure_out_option(args.result, self.input_file)
        args.result_id = _figure_out_option(args.result_id, self.input_file)
        args.test = _figure_out_option(args.test, self.input_file)
        args.version = _figure_out_option(args.version, self.input_file)

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
        _check_response(self.logger, current_doc_in_es)
        current_doc_in_es = current_doc_in_es.json()

        if current_doc_in_es["hits"]["total"]["value"] > 0:
            print(
                f"Result test={args.test} and result_id={args.result_id} already there, skipping upload"
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
        _check_response(self.logger, response)

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
        parser_upload = subparsers.add_parser(
            "upload",
            help="Upload result to Results Dashboard if it is not there already",
        )
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


class pluginHtml(pluginBase):
    def links(self, args):
        self.logger.info("Downloading {args.url}")
        doc = requests.get(args.url)

        # Regular expression to find all href attributes within <a> tags
        # Cheatsheet:
        #   (?: ... ): Non-capturing group. It groups the pattern inside, but
        #              doesn't store the matched text as a separate capture group.
        #   [^>]*?: Matches anything except '>' zero or more times. The '?'
        #           makes it a non-greedy match so we do not consume href as well.
        href_regex = r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']*)["\']'
        matched_hrefs = re.findall(href_regex, doc.text, re.IGNORECASE)
        self.logger.info(f"Found {len(matched_hrefs)} links")

        # Filter links down as per user provided expression
        compiled_regex = re.compile(args.regexp)
        filtered_hrefs = [href for href in matched_hrefs if compiled_regex.match(href)]
        self.logger.info(f"Filtered links down to {len(filtered_hrefs)} links")

        # Make all the links absolute to initial user provided URL.
        # If there is already absolute link like 'http://www.example.com',
        # it will not be affected
        absolute_hrefs = [urllib.parse.urljoin(args.url, href) for href in filtered_hrefs]

        # Print what we found
        for href in absolute_hrefs:
            print(href)

        return absolute_hrefs

    def set_args(self, parser, subparsers):
        # Options for listing links from the document
        parser_links = subparsers.add_parser(
            "links",
            help="List links from given HTML document (e.g. httpd directory listing)",
        )
        parser_links.set_defaults(func=self.links)
        parser_links.add_argument(
            "--url",
            required=True,
            help="HTML document to parse links from",
        )
        parser_links.add_argument(
            "--regexp",
            default=r".*",
            help="Only return links matching this regexp (defaults to '.*')",
        )


PLUGINS = {
    "prow": pluginProw(),
    "opensearch": pluginOpenSearch(),
    "horreum": pluginHorreum(),
    "resultsdashboard": pluginResultsDashboard(),
    "html": pluginHtml(),
}


def main():
    parser = argparse.ArgumentParser(
        description="Shovel data from A to B",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        dest="plugin_name",
        help="sub-command help",
        required=True,
    )
    for name, plugin in PLUGINS.items():
        parser_plugin = subparsers.add_parser(
            name,
            help=f"Work with {name}",
        )
        subparsers_plugin = parser_plugin.add_subparsers(
            dest="plugin_command",
            help="sub-command help",
            required=True,
        )
        plugin.set_args(parser_plugin, subparsers_plugin)

    with skelet.test_setup(parser) as (args, status_data):
        args.func(args)


if __name__ == "__main__":
    main()
