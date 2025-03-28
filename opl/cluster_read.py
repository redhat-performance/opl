import logging
import argparse
import csv
import yaml
import json
import subprocess
import re
import requests
import os
import jinja2
import jinja2.exceptions
import boto3
import urllib3
import tempfile

from . import data
from . import date
from . import status_data
from . import retry


def execute(command):
    p = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if p.returncode != 0 or len(p.stderr) != 0:
        stderr = p.stderr.decode().strip().replace("\n", "\t")
        stdout = p.stdout.decode().strip().replace("\n", "\t")
        logging.error(
            f"Failed to execute command '{command}' - returned stdout '{stdout}', stderr '{stderr}' and returncode '{p.returncode}'"
        )
        result = None
    else:
        result = p.stdout.decode().strip()

    return result


def redact_sensitive_headers(data: dict):
    # Lower-case list of sensitive data in header
    sensitive_headers = ["authorization", "set-cookie", "x-api-key", "cookie"]

    redacted_headers = {}
    for header, value in data.items():
        if header.lower() in sensitive_headers:
            redacted_headers[header] = "<REDACTED>"
        else:
            redacted_headers[header] = value
    return redacted_headers


def _debug_response(r):
    """
    Print various info about the requests response. Should be called when
    request failed
    """
    logging.error("URL = %s" % r.url)
    logging.error("Request headers = %s" % redact_sensitive_headers(r.request.headers))
    logging.error("Response headers = %s" % redact_sensitive_headers(r.headers))
    logging.error("Response status code = %s" % r.status_code)
    logging.error("Response content = %s" % r.content[:500])
    raise Exception("Request failed")


def dir_path(path):
    """
    Utility function to be used in Argparse to check for argument is a directory.
    """
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"{path} is not directory")


class BasePlugin:
    def __init__(self, args):
        self.args = args

    def measure(self, ri, **args):
        pass

    def _dump_raw_data(self, name, mydata):
        """
        Dumps raw data for monitoring plugins into CSV files (first column
        for timestamp, second for value) into provided directory.
        """
        if self.args.monitoring_raw_data_dir is None:
            return

        file_name = re.sub("[^a-zA-Z0-9-]+", "_", name) + ".csv"
        file_path = os.path.join(self.args.monitoring_raw_data_dir, file_name)

        logging.debug(f"Dumping raw data ({len(mydata)} rows) to {file_path}")
        with open(file_path, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["timestamp", name])
            csvwriter.writerows(mydata)

    @staticmethod
    def add_args(parser):
        pass


class PrometheusMeasurementsPlugin(BasePlugin):
    def _get_token(self):
        if self.args.prometheus_token is None:
            self.args.prometheus_token = execute("oc whoami -t")
            if self.args.prometheus_token is None:
                raise Exception("Failsed to get token")
        return self.args.prometheus_token

    def measure(self, ri, name, monitoring_query, monitoring_step):
        logging.debug(
            f"/Getting data for {name} using Prometheus query {monitoring_query} and step {monitoring_step}"
        )

        assert (
            ri.start is not None and ri.end is not None
        ), "We need timerange to approach Prometheus"
        # Get data from Prometheus
        url = f"{self.args.prometheus_host}:{self.args.prometheus_port}/api/v1/query_range"
        headers = {
            "Content-Type": "application/json",
        }
        if not self.args.prometheus_no_auth:
            headers["Authorization"] = f"Bearer {self._get_token()}"
        params = {
            "query": monitoring_query,
            "step": monitoring_step,
            "start": ri.start.timestamp(),
            "end": ri.end.timestamp(),
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(
            url, headers=headers, params=params, verify=False, timeout=60
        )
        if not response.ok or response.headers["Content-Type"] != "application/json":
            _debug_response(response)

        # Check that what we got back seems OK
        json_response = response.json()
        logging.debug("Response: %s" % json_response)
        assert json_response["status"] == "success", "'status' needs to be 'success'"
        assert "data" in json_response, "'data' needs to be in response"
        assert (
            "result" in json_response["data"]
        ), "'result' needs to be in response's 'data'"
        assert (
            len(json_response["data"]["result"]) != 0
        ), "missing 'response' in response's 'data'"
        assert (
            len(json_response["data"]["result"]) == 1
        ), "we need exactly one 'response' in response's 'data'"
        assert (
            "values" in json_response["data"]["result"][0]
        ), "we need expected form of response"

        mydata = [
            (i[0], float(i[1])) for i in json_response["data"]["result"][0]["values"]
        ]
        stats = data.data_stats([i[1] for i in mydata])
        self._dump_raw_data(name, mydata)
        return name, stats

    @staticmethod
    def add_args(parser):
        parser.add_argument(
            "--prometheus-host",
            default="https://prometheus-k8s.openshift-monitoring.svc",
            help="Prometheus server to talk to",
        )
        parser.add_argument(
            "--prometheus-port",
            type=int,
            default=9091,
            help="Port Prometheus is listening on",
        )
        parser.add_argument(
            "--prometheus-token",
            default=None,
            help='Authorization token without the "Bearer: " part. If not provided, we will try to get one with "oc whoami -t"',
        )
        parser.add_argument(
            "--prometheus-no-auth",
            action="store_true",
            help="Do not send auth headers to Prometheus",
        )


class GrafanaMeasurementsPlugin(BasePlugin):
    def _sanitize_target(self, target):
        target = target.replace("$Node", self.args.grafana_node)
        target = target.replace("$Interface", self.args.grafana_interface)
        target = target.replace("$Cloud", self.args.grafana_prefix)
        return target

    @retry.retry_on_traceback(max_attempts=10, wait_seconds=1)
    def measure(self, ri, name, grafana_target, grafana_enritchment={}, grafana_include_vars=False):
        assert (
            ri.start is not None and ri.end is not None
        ), "We need timerange to approach Grafana"
        if ri.start.strftime("%s") == ri.end.strftime("%s"):
            return name, None

        # Metadata for the request
        headers = {
            "Accept": "application/json, text/plain, */*",
        }
        if self.args.grafana_token is not None:
            headers["Authorization"] = "Bearer %s" % self.args.grafana_token
        params = {
            "target": [self._sanitize_target(grafana_target)],
            "from": int(ri.start.timestamp()),
            "until": round(ri.end.timestamp()),
            "format": "json",
        }
        url = f"{self.args.grafana_host}:{self.args.grafana_port}/api/datasources/proxy/{self.args.grafana_datasource}/render"

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.post(
            url=url, headers=headers, params=params, timeout=60, verify=False
        )
        if (
            not r.ok
            or r.headers["Content-Type"] != "application/json"
            or r.json() == []
        ):
            _debug_response(r)
        logging.debug("Response: %s" % r.json())

        points = [float(i[0]) for i in r.json()[0]["datapoints"] if i[0] is not None]
        stats = data.data_stats(points)

        # Add user defined data to the computed stats
        if grafana_enritchment is not None and grafana_enritchment != {}:
            stats["enritchment"] = grafana_enritchment

        # If requested, add info about what variables were used to the computed stats
        if grafana_include_vars:
            stats["variables"] = {
                "$Node": self.args.grafana_node,
                "$Interface": self.args.grafana_interface,
                "$Cloud": self.args.grafana_prefix,
            }

        return name, stats

    @staticmethod
    def add_args(parser):
        parser.add_argument(
            "--grafana-host", default="", help="Grafana server to talk to"
        )
        parser.add_argument(
            "--grafana-chunk-size",
            type=int,
            default=10,
            help="How many metrices to obtain from Grafana at one request",
        )
        parser.add_argument(
            "--grafana-port",
            type=int,
            default=11202,
            help="Port Grafana is listening on",
        )
        parser.add_argument(
            "--grafana-prefix",
            default="satellite62",
            help="Prefix for data in Graphite",
        )
        parser.add_argument(
            "--grafana-datasource", type=int, default=1, help="Datasource ID in Grafana"
        )
        parser.add_argument(
            "--grafana-token",
            default=None,
            help='Authorization token without the "Bearer: " part',
        )
        parser.add_argument(
            "--grafana-node",
            default="satellite_satperf_local",
            help="Monitored host node name in Graphite",
        )
        parser.add_argument(
            "--grafana-interface",
            default="interface-em1",
            help="Monitored host network interface name in Graphite",
        )


class PerformanceInsightsMeasurementPlugin(BasePlugin):
    def get_formatted_metric_query(self, metric_query):
        return [{"Metric": metric_query}]

    def measure(self, requested_info, name, identifier, metric_query, metric_step):
        logging.debug(
            f"/Getting data for {identifier} using PI query {metric_query} with monitoring interval {metric_step}"
        )

        assert (
            requested_info.start is not None and requested_info.end is not None
        ), "We need timerange to approach AWS PI service"

        assert (
            self.args.aws_pi_access_key_id is not None
            and self.args.aws_pi_secret_access_key is not None
        ), "We need AWS access key and secret key to create the client for accessing PI service"

        # Create a low-level service client
        aws_session = boto3.session.Session(
            aws_access_key_id=self.args.aws_pi_access_key_id,
            aws_secret_access_key=self.args.aws_pi_secret_access_key,
            region_name=self.args.aws_pi_region_name,
        )
        aws_client = aws_session.client("pi")
        response = aws_client.get_resource_metrics(
            ServiceType="RDS",
            Identifier=identifier,
            StartTime=requested_info.start,
            EndTime=requested_info.end,
            MetricQueries=self.get_formatted_metric_query(metric_query),
            PeriodInSeconds=metric_step,
        )

        # Check that what we got back seems OK
        logging.debug(f"Response: {response}")
        assert len(response["MetricList"]) > 0, "'MetricList' should not be empty"
        assert (
            response["MetricList"][0]["Key"]["Metric"] == metric_query
        ), "'metric_query' needs to be in response"
        assert (
            len(response["MetricList"][0]["DataPoints"]) > 0
        ), "'DataPoints' needs to be in response"

        points = [
            data_point["Value"]
            for data_point in response["MetricList"][0]["DataPoints"]
            if "Value" in data_point
        ]
        if len(points) < len(response["MetricList"][0]["DataPoints"]):
            logging.info(
                f"Value is missing in the AWS PI datapoints, total data points: {len(response['MetricList'][0]['DataPoints'])}, available values: {len(points)}"
            )
        stats = data.data_stats(points)
        return name, stats

    @staticmethod
    def add_args(parser):
        parser.add_argument(
            "--aws-pi-access-key-id",
            default=os.getenv("AWS_PI_READ_ONLY_ACCESS_KEY_ID"),
            help="The aws access key to use when creating the client for accessing PI service",
        )
        parser.add_argument(
            "--aws-pi-secret-access-key",
            default=os.getenv("AWS_PI_READ_ONLY_SECRET_ACCESS_KEY"),
            help="The aws secret key to use when creating the client for accessing PI service",
        )
        parser.add_argument(
            "--aws-pi-region-name",
            default="us-east-1",
            help="The name of the aws region associated with the client",
        )


class ConstantPlugin(BasePlugin):
    def measure(self, ri, name, constant):
        """
        Just store given constant
        """
        return name, constant


class EnvironmentPlugin(BasePlugin):
    def measure(self, ri, name, env_variable):
        """
        Just get value of given environment variable
        """
        return name, os.environ.get(env_variable, None)


class CommandPlugin(BasePlugin):
    def measure(self, ri, name, command, output="text"):
        """
        Execute command "command" and return result as per its "output" configuration
        """
        # Execute the command
        result = execute(command)

        # Sanitize command response
        if result is not None:
            if output == "text":
                pass
            elif output == "json":
                result = json.loads(result)
            elif output == "yaml":
                result = yaml.load(result, Loader=yaml.SafeLoader)
            else:
                raise Exception(f"Unexpected output type '{output}' for '{name}'")

        return name, result


class CountLinePlugin(BasePlugin):
    def measure(
        self,
        ri,
        config,
        output="text",
    ):
        """
        Execute command "command" and return result as per its "output" configuration
        """
        name = config["name"]
        log_source_command = config["log_source_command"]
        result = execute(log_source_command).splitlines()

        output = {}
        output["all"] = len(result)

        for pattern_name, pattern_value in config.items():
            if not pattern_name.startswith("log_regexp_"):
                continue
            pattern_key = pattern_name[len("log_regexp_") :]
            pattern_regexp = re.compile(pattern_value)
            counter = 0
            for line in result:
                if pattern_regexp.search(line):
                    counter += 1
            output[pattern_key] = counter

        return name, output


class CopyFromPlugin(BasePlugin):
    def measure(self, ri, name, copy_from):
        """
        Just return value from previously answered item
        """
        if ri.sd is None:
            return name, None
        else:
            return name, ri.sd.get(copy_from)


class TestFailMePlugin(BasePlugin):
    def measure(self, ri, name, **kwargs):
        """
        Just raise an exception. Mean for tests only.
        """
        _ = 1 / 0


PLUGINS = {
    "test_fail_me": TestFailMePlugin,
    "constant": ConstantPlugin,
    "env_variable": EnvironmentPlugin,
    "command": CommandPlugin,
    "copy_from": CopyFromPlugin,
    "log_source_command": CountLinePlugin,
    "monitoring_query": PrometheusMeasurementsPlugin,
    "grafana_target": GrafanaMeasurementsPlugin,
    "metric_query": PerformanceInsightsMeasurementPlugin,
}


def config_stuff(config):
    """
    "config" is yaml loadable stuff - either opened file object, or string
        containing yaml formated data. First of all we will run it through
        Jinja2 as a template with env variables to expand
    """

    class MyLoader(jinja2.BaseLoader):
        """
        Our custom wide open and possibly unsecure jinja2 loader

        Main template is stored as a string, but also capable of loading
        templates to satisfy things like:

            {% extends "../something.yaml" %}

        or:

            {% import '../something.yaml' as something %}

        It is very similar to `jinja2.FileSystemLoader('/')` but can also
        handle loading files with relative path.
        """

        def __init__(self, main_template):
            self.main_template = main_template

        def get_source(self, environment, path):
            if path == "main_template":
                return self.main_template, None, lambda: True

            if not os.path.exists(path):
                raise jinja2.exceptions.TemplateNotFound(path)

            mtime = os.path.getmtime(path)
            with open(path) as f:
                source = f.read()

            return source, path, lambda: mtime == os.path.getmtime(path)

    if not isinstance(config, str):
        config = config.read()

    env = jinja2.Environment(loader=MyLoader(config))
    template = env.get_template("main_template")

    config_rendered = template.render(os.environ)
    return yaml.load(config_rendered, Loader=yaml.SafeLoader)


class RequestedInfo:
    def __init__(
        self, config, start=None, end=None, args=argparse.Namespace(), sd=None
    ):
        """
        "config" is input for config_stuff function
        "start" and "end" are datetimes needed if config file contains some
            monitoring items to limit from and to time of returned monitoring
            data
        """
        self.config = config_stuff(config)
        self.start = start
        self.end = end
        self.args = args
        self.sd = sd

        self._index = 0  # which config item are we processing?
        self._token = None  # OCP token - we will take it from `oc whoami -t` if needed
        self.measurement_plugins = (
            {}
        )  # objects to use for measurements (it's 'measure()' method) by key in config

        # Register plugins
        for name, plugin in PLUGINS.items():
            try:
                self.register_measurement_plugin(name, plugin(args))
            except Exception as e:
                logging.warning(f"Failed to register plugin {name}: {e}")

    def register_measurement_plugin(self, key, instance):
        self.measurement_plugins[key] = instance

    def get_config(self):
        return self.config

    def __iter__(self):
        return self

    def _find_plugin(self, keys):
        for key in keys:
            if key in self.measurement_plugins:
                return self.measurement_plugins[key]
        return False

    def __next__(self):
        """
        Gives tuple of key and value for every item in the config file
        """
        i = self._index
        self._index += 1
        if i < len(self.config):
            if self._find_plugin(self.config[i].keys()):
                instance = self._find_plugin(self.config[i].keys())
                name = list(self.config[i].keys())[1]
                try:
                    if name == "log_source_command":
                        output = instance.measure(self, self.config[i])
                    else:
                        output = instance.measure(self, **self.config[i])
                except Exception as e:
                    logging.exception(
                        f"Failed to measure {self.config[i]['name']}: {e}"
                    )
                    output = (None, None)
                return output
            else:
                raise Exception(f"Unknown config '{self.config[i]}'")
        else:
            raise StopIteration


def doit(args):
    if args.requested_info_string:
        config = f"""
            - name: requested-info-string
              command: {args.requested_info_string}
              output: {args.requested_info_outputtype}
        """
    else:
        config = args.requested_info_config

    sd = status_data.StatusData(tempfile.NamedTemporaryFile().name)

    requested_info = RequestedInfo(
        config,
        args.monitoring_start,
        args.monitoring_end,
        args=args,
        sd=sd,
    )

    if args.render_config:
        print(yaml.dump(requested_info.get_config(), width=float("inf")))
    else:
        for k, v in requested_info:
            print(f"{k}: {v}")


def main():
    parser = argparse.ArgumentParser(
        description="Run commands defined in a config file and show output",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--requested-info-config",
        type=argparse.FileType("r"),
        help="File with list of commands to run",
    )
    parser.add_argument(
        "--requested-info-string", help="Ad-hoc command you want to run"
    )
    parser.add_argument(
        "--requested-info-outputtype",
        default="text",
        choices=["text", "json", "yaml"],
        help='Ad-hoc command output type, default to "text"',
    )
    parser.add_argument(
        "--monitoring-start",
        type=date.my_fromisoformat,
        help="Start of monitoring interval in ISO 8601 format in UTC with seconds precision",
    )
    parser.add_argument(
        "--monitoring-end",
        type=date.my_fromisoformat,
        help="End of monitoring interval in ISO 8601 format in UTC with seconds precision",
    )
    parser.add_argument(
        "--monitoring-raw-data-dir",
        type=dir_path,
        help="Provide a direcotory if you want raw monitoring data to be dumped in CSV files form",
    )
    parser.add_argument(
        "--render-config", action="store_true", help="Just render config"
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    for name, plugin in PLUGINS.items():
        plugin.add_args(parser)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.requested_info_config is None and args.requested_info_string is None:
        logging.error(
            "At least one of '--requested-info-config' or '--requested-info-string' needs to be set"
        )
        return 1
    if (
        args.requested_info_config is not None
        and args.requested_info_string is not None
    ):
        logging.error(
            "Only one of '--requested-info-config' or '--requested-info-string' can be set"
        )
        return 1

    logging.debug(f"Args: {args}")

    doit(args)
