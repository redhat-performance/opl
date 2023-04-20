import argparse
import datetime
import json
import logging
import os
import unicodedata
import junitparser
import urllib3

import requests

from . import date


def now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


class TestCaseWithProp(junitparser.TestCase):
    def properties(self):
        """
        Iterates through all properties.
        """
        props = self.child(junitparser.Properties)
        if props is None:
            return
        for prop in props:
            yield prop

    def add_property(self, name, value):
        """
        Adds a property to the testsuite.
        """
        props = self.child(junitparser.Properties)
        if props is None:
            props = junitparser.Properties()
            self.append(props)
        prop = junitparser.Property(name, value)
        props.add_property(prop)

    def get_property(self, name, default=None):
        """
        Get a property from the testcase
        """
        for prop in self.properties():
            if prop.name == name:
                return prop.value
        return default


class JUnitXmlPlus(junitparser.JUnitXml):
    @classmethod
    def fromfile_or_new(cls, filename):
        if os.path.exists(filename):
            instance = cls.fromfile(filename)
        else:
            instance = cls()
            instance.filepath = filename
        return instance

    def _remove_control_characters(self, s):
        return "".join(
            ch for ch in s if unicodedata.category(ch)[0] != "C" or ch == "\n"
        )

    def add_to_suite(self, suite_name, new):
        case = TestCaseWithProp(new["name"])

        suite_found = False
        for suite in self:
            if suite.name == suite_name:
                logging.debug(f"Suite {suite_name} found, going to add into it")
                suite_found = True
        if not suite_found:
            logging.debug(f"Suite {suite_name} not found, creating new one")
            suite = junitparser.TestSuite(suite_name)
            self.add_testsuite(suite)

        if new["result"] == "PASS":
            case.result = []
        elif new["result"] == "FAIL":
            case.result = [junitparser.Failure(new["message"])]
        elif new["result"] == "ERROR":
            case.result = [junitparser.Error(new["message"])]
        else:
            raise Exception(f"Invalid result {new['result']}")

        case.system_out = ""
        if new["system-out"]:
            for f in new["system-out"]:
                try:
                    case.system_out += self._remove_control_characters(f.read())
                    case.system_out += "\n"
                except ValueError as e:
                    logging.error(f"Failed to load {new['system-out'].name} file: {e}")
        case.system_err = ""
        if new["system-err"]:
            for f in new["system-err"]:
                try:
                    case.system_err += self._remove_control_characters(f.read())
                    case.system_err += "\n"
                except ValueError as e:
                    logging.error(f"Failed to load {new['system-err'].name} file: {e}")

        duration = (new["end"] - new["start"]).total_seconds()
        case.time = duration

        case.add_property("start", new["start"].isoformat())
        case.add_property("end", new["end"].isoformat())

        suite.add_testcase(case)

        self.write()

    def get_info(self):
        out = []
        for suite in self:
            print(f"suite: {suite}")
            for prop in suite.properties():
                print(f"    property: {prop}")
            for case in suite:
                case = TestCaseWithProp.fromelem(case)
                print(f"    case: {case}   {case.result}")
                for prop in case.properties():
                    print(f"        property: {prop}")
        return "\n".join(out)

    def get_result(self):
        RESULTS = ["PASSED", "SKIPPED", "FAILED", "ERROR"]
        result = 0
        for suite in self:
            for case in suite:
                case = TestCaseWithProp.fromelem(case)
                if len(case.result) == 0:
                    pass  # result "PASS" can not make overall result worse
                elif len(case.result) == 1:
                    r = case.result[0]
                    if isinstance(r, junitparser.junitparser.Error):
                        result = max(result, 3)
                    elif isinstance(r, junitparser.junitparser.Failure):
                        result = max(result, 2)
                    elif isinstance(r, junitparser.junitparser.Skipped):
                        result = max(result, 1)
                    else:
                        raise Exception(
                            f"No idea how to handle this result type: {r} - {type(r)}"
                        )
                else:
                    raise Exception(
                        f"No idea how to handle this case result: {case.result}"
                    )
        return RESULTS[result]

    def delete(self):
        os.remove(self.filepath)

    def ibutsu_upload(self, host, token, project, verify, file, metadata):
        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        headers = {"Authorization": f"Bearer {token}"}
        if metadata:
            metadata = json.dumps(self.parse_ibutsu_metadata(metadata))
        res = requests.post(
            f"{host}/api/import",
            headers=headers,
            files={
                "importFile": (file, open(file, "rb"), "text/xml"),
            },
            verify=verify,
            data={"project": project, "metadata": metadata},
        )
        if not res.ok:
            raise Exception(res.text)
        else:
            logging.debug(res.text)

    def parse_ibutsu_metadata(self, metadata_list):
        """Parse the metadata from a set of strings to a dictionary"""
        metadata = {}
        # Loop through the list of metadata values
        for pair in metadata_list:
            # Split the key part from the value
            key_path, value = pair.split("=", 1)
            # Split the key up if it is a dotted path
            keys = key_path.split(".")
            current_data = metadata
            # Loop through all but the last key and create the dictionary structure
            for key in keys[:-1]:
                if key not in current_data:
                    current_data[key] = {}
                current_data = current_data[key]
            # Finally, set the actual value
            key = keys[-1]
            current_data[key] = value
        return metadata

    def upload(self, host, verify, project, token, launch, properties):
        def req(method, url, data):
            logging.debug(f"Going to do {method} request to {url} with {data}")
            response = method(url, json=data, headers=headers, verify=verify)
            if not response.ok:
                logging.error(f"Request failed: {response.text}")
            response.raise_for_status()
            logging.debug(f"Request returned {response.json()}")
            return response.json()

        def times(ts):
            return str(int(ts.timestamp() * 1000))

        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Determine launch start and end by taking min from test case
        # starts and max from testcase ends
        start = None
        end = None
        suites_times = {}
        for suite in self:
            suite_start = None
            suite_end = None
            for case in suite:
                case = TestCaseWithProp.fromelem(case)
                for prop in case.properties():
                    if prop.name == "start":
                        tmp = date.my_fromisoformat(prop.value)
                        if start is None or start > tmp:
                            start = tmp
                        if suite_start is None or suite_start > tmp:
                            suite_start = tmp
                    if prop.name == "end":
                        tmp = date.my_fromisoformat(prop.value)
                        if end is None or end < tmp:
                            end = tmp
                        if suite_end is None or suite_end < tmp:
                            suite_end = tmp
            suite_start = suite_start if suite_start is not None else now()
            suite_end = suite_end if suite_end is not None else now()
            suites_times[suite.name] = [suite_start, suite_end]
        start = start if start is not None else now()
        end = end if end is not None else now()

        # Start a session
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        session = requests.Session()

        # Start launch
        url = f"https://{host}/api/v1/{project}/launch"
        data = {
            "name": launch,
            "startTime": times(start),
            "mode": "DEFAULT",
            "attributes": [],
        }
        for prop in properties:
            name, value = prop.split("=")
            data["attributes"].append(
                {
                    "key": name,
                    "value": value,
                }
            )
        response = req(session.post, url, data)
        launch_id = response["id"]

        # Process all the suites
        for suite in self:
            suite_start, suite_end = suites_times[suite.name]

            # Start root(suite) item
            url = f"https://{host}/api/v1/{project}/item"
            data = {
                "name": suite.name,
                "startTime": times(suite_start),
                "type": "suite",
                "launchUuid": launch_id,
                "attributes": [],
            }
            for prop in suite.properties():
                data["attributes"].append(
                    {
                        "key": prop.name,
                        "value": prop.value,
                    }
                )
            response = req(session.post, url, data)
            suite_id = response["id"]

            # Process all the testcases in the suite
            for case in suite:
                case = TestCaseWithProp.fromelem(case)
                case_start = date.my_fromisoformat(case.get_property("start", now()))
                case_end = date.my_fromisoformat(case.get_property("end", now()))

                # Determine case status
                if len(case.result) == 0:
                    result = "passed"
                    issue = None
                elif isinstance(case.result[0], junitparser.junitparser.Error):
                    result = "failed"
                    issue = "si001"
                elif isinstance(case.result[0], junitparser.junitparser.Failure):
                    result = "failed"
                    issue = "ti001"
                elif isinstance(case.result[0], junitparser.junitparser.Skipped):
                    result = "skipped"
                    issue = "ti001"
                else:
                    raise Exception(f"Unknown result for {case}: {case.result}")

                # Start child(container) item
                url = f"https://{host}/api/v1/{project}/item/{suite_id}"
                data = {
                    "name": case.name,
                    "startTime": times(case_start),
                    "type": "test",
                    "launchUuid": launch_id,
                    "attributes": [],
                }
                for prop in case.properties():
                    data["attributes"].append(
                        {
                            "key": prop.name,
                            "value": prop.value,
                        }
                    )
                response = req(session.post, url, data)
                case_id = response["id"]

                # Finish parent(container) item
                url = f"https://{host}/api/v1/{project}/item/{case_id}"
                data = {
                    "endTime": times(case_end),
                    "launchUuid": launch_id,
                    "status": result,
                }
                if issue is not None:
                    data["issue"] = {"issueType": issue}
                response = req(session.put, url, data)

                # Add log message
                url = f"https://{host}/api/v1/{project}/log"
                data = {
                    "launchUuid": launch_id,
                    "itemUuid": case_id,
                    "time": times(case_end),
                    "message": case.system_out,
                    "level": "info",
                }
                response = req(session.post, url, data)
                if case.system_err:
                    data["message"] = case.system_err
                    data["level"] = "error"
                    response = req(session.post, url, data)

            # Finish root(suite) item
            url = f"https://{host}/api/v1/{project}/item/{suite_id}"
            data = {
                "endTime": times(suite_end),
                "launchUuid": launch_id,
            }
            response = req(session.put, url, data)

        # Finish launch
        url = f"https://{host}/api/v1/{project}/launch/{launch_id}/finish"
        data = {
            "endTime": times(end),
        }
        response = req(session.put, url, data)

        # Show where we have uploaded data
        print(f"Created launch https://{host}/ui/#{project}/launches/all/{launch_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Manipulate jUnit file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--file",
        default=os.getenv("JUNIT_FILE", "junit.xml"),
        help="jUnit file to work with (also use env variable JUNIT_FILE)",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    subparsers = parser.add_subparsers(dest="action", help="Select one of sub-commands")

    # Create the parser for the "print" command
    subparsers.add_parser("print", help="Print content of the file")  # noqa: F841

    # Create the parser for the "result" command
    subparsers.add_parser(
        "result", help="Print overall result from the file"  # noqa: F841
    )

    # create the parser for the "add" command
    parser_add = subparsers.add_parser("add", help="Add testcase into the file")
    parser_add.add_argument("--name", required=True, help="Name of the testcase")
    parser_add.add_argument(
        "--result",
        required=True,
        choices=["PASS", "FAIL", "ERROR"],
        help="Result of the testcase",
    )
    parser_add.add_argument(
        "--suite", required=True, help="Testsuite this testcase should be in"
    )
    parser_add.add_argument(
        "--out",
        type=argparse.FileType("r"),
        nargs="*",
        default=[],
        help="File with stdout of the testcase",
    )
    parser_add.add_argument(
        "--err",
        type=argparse.FileType("r"),
        nargs="*",
        default=[],
        help="File with stderr of the testcase",
    )
    parser_add.add_argument("--message", help="Message when result is failure or error")
    parser_add.add_argument(
        "--start",
        required=True,
        type=date.my_fromisoformat,
        help="Testcase start time in ISO 8601 format",
    )
    parser_add.add_argument(
        "--end",
        required=True,
        type=date.my_fromisoformat,
        help="Testcase end time in ISO 8601 format",
    )

    # create the parser for the "ibutsu" command
    parser_ibutsu = subparsers.add_parser(
        "ibutsu-import", help="Import the file to Ibutsu"
    )
    parser_ibutsu.add_argument("--host", required=True, help="Ibutsu host")
    parser_ibutsu.add_argument("--token", required=True, help="Ibutsu token")
    parser_ibutsu.add_argument("--project", required=True, help="Ibutsu project")
    parser_ibutsu.add_argument(
        "--noverify",
        action="store_true",
        help="When talking to Ibutsu ignore certificate verification failures",
    )
    parser_ibutsu.add_argument(
        "--metadata",
        action="append",
        help="Additional metadata to set when uploading, in the format of dotted.key.path=value",
    )

    # create the parser for the "upload" command
    parser_add = subparsers.add_parser("upload", help="Upload the file to ReportPortal")
    parser_add.add_argument("--host", required=True, help="ReportPortal host")
    parser_add.add_argument(
        "--noverify",
        action="store_true",
        help="When talking to ReportPortal ignore certificate verification failures",
    )
    parser_add.add_argument("--project", required=True, help="ReportPortal project")
    parser_add.add_argument("--token", required=True, help="ReportPortal token")
    parser_add.add_argument(
        "--launch", required=True, help="ReportPortal launch name to use when creating"
    )
    parser_add.add_argument(
        "--properties",
        nargs="*",
        default=[],
        help="Launch property pairs in a name=value form, space separated, that will be added as ReportPortal attributes",
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    junit = JUnitXmlPlus.fromfile_or_new(args.file)

    if args.action == "print":
        print(junit.get_info())
    elif args.action == "result":
        print(junit.get_result())
    elif args.action == "add":
        new = {
            "name": args.name,
            "result": args.result,
            "system-out": args.out,
            "system-err": args.err,
            "message": args.message,
            "start": args.start,
            "end": args.end,
        }
        junit.add_to_suite(args.suite, new)
    elif args.action == "upload":
        junit.upload(
            args.host,
            not args.noverify,
            args.project,
            args.token,
            args.launch,
            args.properties,
        )
    elif args.action == "ibutsu-import":
        junit.ibutsu_upload(
            args.host,
            args.token,
            args.project,
            not args.noverify,
            args.file,
            args.metadata,
        )
    else:
        raise Exception("I do not know what to do")
