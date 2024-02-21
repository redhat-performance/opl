#!/usr/bin/env python3


# Copyright 2024 Bard (https://huggingface.co/bard)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import unittest.mock
import pytest
import subprocess
import os
import csv
import logging
import argparse
import pd
import requests
import boto3
from collections import namedtuple

# Move import statements to beginning of each file

# BasePlugin
from ..BasePlugin import BasePlugin
from ..data import data

# PerformanceInsightsMeasurementPlugin
from ..aws_client import get_resource_metrics

# Test plugins
from .ConstantPlugin import ConstantPlugin
from .EnvironmentPlugin import EnvironmentPlugin
from .CommandPlugin import CommandPlugin
from .CopyFromPlugin import CopyFromPlugin
from .TestFailMePlugin import TestFailMePlugin
from .config_stuff import config_stuff
from .RequestedInfo import RequestedInfo


def test_execute_success(mocker):
    # Patch subprocess.run to return success
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["echo", "hello"], stdout=b"hello\n", stderr=b"", returncode=0
        ),
    )
    # Call the function
    result = execute("echo hello")
    # Assert result and no logging errors
    assert result == "hello"
    assert not logging.getEffectiveLevel() == logging.ERROR


def test_execute_failure_with_stdout(mocker):
    # Patch subprocess.run to return failure with stdout
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["invalid_command"], stdout=b"some error message\n", stderr=b"", returncode=1
        ),
    )
    # Capture logging calls
    with capture_logs() as log_records:
        execute("invalid_command")
    # Assert logging error with expected message
    assert any(
        record.level == logging.ERROR
        and "Failed to execute command" in record.message
        for record in log_records
    )


def test_execute_failure_with_stderr(mocker):
    # Patch subprocess.run to return failure with stderr
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["invalid_command"], stdout=b"", stderr=b"some error message\n", returncode=1
        ),
    )
    # Capture logging calls
    with capture_logs() as log_records:
        execute("invalid_command")
    # Assert logging error with expected message
    assert any(
        record.level == logging.ERROR
        and "Failed to execute command" in record.message
        for record in log_records
    )


def test_execute_empty_command(mocker):
    # Patch subprocess.run to be called with empty command
    mocker.patch("subprocess.run")
    # Call the function
    with pytest.raises(ValueError):
        execute("")


def test_execute_non_string_command(mocker):
    # Patch subprocess.run to be called with non-string command
    mocker.patch("subprocess.run")
    # Call the function
    with pytest.raises(TypeError):
        execute(123)



def test_debug_response_with_response():
    # Mock response object with attributes
    response = Mock()
    response.url = "https://example.com"
    response.request.headers = {"Content-Type": "application/json"}
    response.headers = {"Server": "nginx"}
    response.status_code = 404
    response.content = b"Not Found"

    # Capture expected logged messages
    expected_logs = [
        f"URL = {response.url}",
        f"Request headers = {response.request.headers}",
        f"Response headers = {response.headers}",
        f"Response status code = {response.status_code}",
        f"Response content = {response.content[:500]}",
    ]

    # Call the function and assert raised exception
    with pytest.raises(Exception) as exc_info:
        _debug_response(response)
    assert exc_info.value.args[0] == "Request failed"

    # Assert logged messages
    for log_record in logging.getLogger().handlers[0].buffer:
        assert log_record.message in expected_logs



def test_dir_path_existing_directory(mocker):
    # Mock os.path.isdir to return True for existing directory
    mocker.patch("os.path.isdir", return_value=True)
    # Test with existing directory
    path = "/path/to/existing/directory"
    result = dir_path(path)
    # Assert returned path and no exceptions
    assert result == path
    assert not pytest.raises(Exception, dir_path, path)


def test_dir_path_non_existing_directory(mocker):
    # Mock os.path.isdir to return False for non-existing directory
    mocker.patch("os.path.isdir", return_value=False)
    # Test with non-existing directory
    path = "/path/to/nonexistent/directory"
    # Assert raised exception with expected message
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        dir_path(path)
    assert f"{path} is not directory" in str(exc_info.value)


def test_dir_path_invalid_path(mocker):
    # Mock os.path.isdir to handle invalid path
    mocker.patch("os.path.isdir", side_effect=OSError("Invalid path"))
    # Test with invalid path
    path = "/invalid/path"
    # Assert raised exception with expected message
    with pytest.raises(OSError) as exc_info:
        dir_path(path)
    assert "Invalid path" in str(exc_info.value)


def test_dir_path_non_string_path():
    # Test with non-string path
    path = 123
    # Assert raised TypeError
    with pytest.raises(TypeError):
        dir_path(path)



class TestBasePlugin:

    @pytest.fixture
    def plugin(self):
        args = Mock()
        args.monitoring_raw_data_dir = "/tmp/data"  # Set a default directory
        return BasePlugin(args)

    @patch("os.path.isdir")
    @patch("os.makedirs")
    def test_dump_raw_data_creates_dir(self, mock_makedirs, mock_isdir, plugin):
        mock_isdir.return_value = False
        data = [["1", "2"], ["3", "4"]]
        plugin._dump_raw_data("mydata", data)
        mock_makedirs.assert_called_once_with("/tmp/data")

    @patch("csv.writer")
    @patch("open")
    def test_dump_raw_data_writes_csv(self, mock_open, mock_csv_writer, plugin):
        data = [["1", "2"], ["3", "4"]]
        plugin._dump_raw_data("mydata", data)
        mock_open.assert_called_once_with("/tmp/data/mydata.csv", "w", newline="")
        mock_csv_writer.assert_has_calls([
            mock.call(["timestamp", "mydata"]),
            mock.call.writerows(data)
        ])

    def test_add_args_does_nothing(self, plugin):
        parser = Mock()
        plugin.add_args(parser)
        parser.add_argument.assert_not_called()



# pylint: disable=unused-argument,redefined-outer-name

class TestGrafanaMeasurementsPlugin(BasePlugin):

    @pytest.fixture
    def plugin(self):
        args = Mock()
        args.grafana_host = "localhost"
        args.grafana_port = 8080
        args.grafana_datasource = 1
        args.grafana_token = "mytoken"
        args.grafana_prefix = "myprefix"
        args.grafana_node = "mynode"
        args.grafana_interface = "myinterface"
        args.monitoring_raw_data_dir = None  # Avoid writing test data
        return GrafanaMeasurementsPlugin(args)

    @patch("requests.post")
    def test_measure_success(self, mock_post, plugin):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"datapoints": [[10, 1654684800]]}]
        mock_post.return_value = mock_response
        ri = Mock()
        ri.start = pd.to_datetime("2022-06-13T10:00:00Z")
        ri.end = pd.to_datetime("2022-06-13T11:00:00Z")
        name = "cpu_usage"
        target = "$Node.$Interface.cpu_usage"
        result, stats = plugin.measure(ri, name, target)
        assert result == name
        assert stats == data.data_stats([10])
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_measure_failure(self, mock_post, plugin):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        ri = Mock()
        ri.start = pd.to_datetime("2022-06-13T10:00:00Z")
        ri.end = pd.to_datetime("2022-06-13T11:00:00Z")
        name = "cpu_usage"
        target = "$Node.$Interface.cpu_usage"
        with pytest.raises(Exception) as exc_info:
            plugin.measure(ri, name, target)
        assert "Request failed" in str(exc_info.value)

    def test_sanitize_target(self, plugin):
        target = "$Node.$Interface.cpu_usage"
        expected = "satellite62.satellite_satperf_local.interface-em1.cpu_usage"
        assert plugin._sanitize_target(target) == expected

    def test_add_args(self, plugin):
        parser = Mock()
        plugin.add_args(parser)
        parser.add_argument.assert_has_calls([
            mock.call("--grafana-host", default="", help="Grafana server to talk to"),
            mock.call("--grafana-chunk-size", type=int, default=10,
                      help="How many metrices to obtain from Grafana at one request"),
            mock.call("--grafana-port", type=int, default=11202,
                      help="Port Grafana is listening on"),
            mock.call("--grafana-prefix", default="satellite62",
                      help="Prefix for data in Graphite"),
            mock.call("--grafana-datasource", type=int, default=1,
                      help="Datasource ID in Grafana"),
            mock.call("--grafana-token", default=None,
                      help='Authorization token without the "Bearer: " part'),
            mock.call("--grafana-node", default="satellite_satperf_local",
                      help="Monitored host node name in Graphite"),
            mock.call("--grafana-interface", default="interface-em1",
                      help="Monitored host network interface name in Graphite"),
        ])



def test_get_formatted_metric_query(self):
    # Test with simple metric query
    metric_query = "CPUUtilization"
    expected_result = [{"Metric": metric_query}]
    assert PerformanceInsightsMeasurementPlugin().get_formatted_metric_query(metric_query) == expected_result

    # Test with multiple metrics
    metric_queries = ["CPUUtilization", "NetworkIn", "NetworkOut"]
    expected_result = [{"Metric": metric} for metric in metric_queries]
    assert PerformanceInsightsMeasurementPlugin().get_formatted_metric_query(metric_queries) == expected_result



@patch("boto3.session.Session")
@patch("aws_client.get_resource_metrics")
def test_measure_success(self, mock_get_resource_metrics, mock_session):
    # Mock successful AWS response
    mock_response = {
        "MetricList": [
            {
                "Key": {"Metric": "CPUUtilization"},
                "DataPoints": [{"Timestamp": 1654684800, "Value": 50}],
            }
        ]
    }
    mock_get_resource_metrics.return_value = mock_response

    # Set up plugin instance with mocked session
    plugin = PerformanceInsightsMeasurementPlugin()
    plugin.args.aws_pi_access_key_id = "my_access_key"
    plugin.args.aws_pi_secret_access_key = "my_secret_key"
    plugin.args.aws_pi_region_name = "us-east-1"
    mock_session.return_value = Mock(client=Mock(return_value=mock_get_resource_metrics()))

    # Call the function with mocked data
    requested_info = Mock()
    requested_info.start = pd.to_datetime("2022-06-13T10:00:00Z")
    requested_info.end = pd.to_datetime("2022-06-13T11:00:00Z")
    identifier = "instance_id"
    metric_query = "CPUUtilization"
    metric_step = 300
    result, stats = plugin.measure(requested_info, "cpu_usage", identifier, metric_query, metric_step)

    # Assert successful execution and data processing
    assert result == "cpu_usage"
    assert stats == data.data_stats([50])

    # Verify function calls and assertions
    mock_get_resource_metrics.assert_called_once_with(
        ServiceType="RDS",
        Identifier=identifier,
        StartTime=requested_info.start,
        EndTime=requested_info.end,
        MetricQueries=[{"Metric": metric_query}],
        PeriodInSeconds=metric_step,
    )
    assert len(logging.getLogger().handlers[0].buffer) == 2  # Expected logging messages

@patch("boto3.session.Session")
@patch("aws_client.get_resource_metrics")
def test_measure_missing_access_keys(self, mock_get_resource_metrics, mock_session):
    # Test with missing access keys
    plugin = PerformanceInsightsMeasurementPlugin()
    plugin.args.aws_pi_region_name = "us-east-1"
    mock_session.return_value = Mock(client=Mock(return_value=mock_get_resource_metrics()))

    # Call the function and expect assertion error
    with pytest.raises(AssertionError):
        plugin.measure(Mock(), "cpu_usage", "instance_id", "CPUUtilization", 300)

@patch("boto3.session.Session")
@patch("aws_client.get_resource_metrics")
def test_measure_empty_response(self, mock_get_resource_metrics, mock_session):
    # Mock empty response from AWS
    mock_response = {"MetricList": []}
    mock_get_resource_metrics.return_value = mock_



def test_constant_plugin(self):
    plugin = ConstantPlugin()
    ri = Mock()
    name = "test_constant"
    constant = "my_value"
    result, value = plugin.measure(ri, name, constant)
    assert result == name
    assert value == constant



def test_environment_plugin_existing_variable(self):
    os.environ["TEST_ENV_VAR"] = "my_value"
    plugin = EnvironmentPlugin()
    ri = Mock()
    name = "test_env_var"
    env_variable = "TEST_ENV_VAR"
    result, value = plugin.measure(ri, name, env_variable)
    assert result == name
    assert value == "my_value"

def test_environment_plugin_missing_variable(self):
    plugin = EnvironmentPlugin()
    ri = Mock()
    name = "test_env_var"
    env_variable = "MISSING_VAR"
    result, value = plugin.measure(ri, name, env_variable)
    assert result == name
    assert value is None



@patch("subprocess.run")
def test_command_plugin_text_output(self, mock_run):
    mock_run.return_value = Mock(stdout=b"this is the output")
    plugin = CommandPlugin()
    ri = Mock()
    name = "test_command"
    command = "echo this is the output"
    result, value = plugin.measure(ri, name, command)
    assert result == name
    assert value == "this is the output"

@patch("subprocess.run")
def test_command_plugin_json_output(self, mock_run):
    mock_run.return_value = Mock(stdout=b'{"key": "value"}')
    plugin = CommandPlugin()
    ri = Mock()
    name = "test_command"
    command = "echo '{\"key\": \"value\"}'"
    output = "json"
    result, value = plugin.measure(ri, name, command, output=output)
    assert result == name
    assert value == {"key": "value"}

# Add similar tests for YAML output and error handling


def test_copy_from_plugin(self):
    ri = Mock()
    ri._responses = {"previous_item": "previous_value"}
    plugin = CopyFromPlugin()
    name = "test_copy"
    copy_from = "previous_item"
    result, value = plugin.measure(ri, name, copy_from)
    assert result == name
    assert value == "previous_value"

def test_copy_from_plugin_missing_item(self):
    ri = Mock()
    ri._responses = {}
    plugin = CopyFromPlugin()
    name = "test_copy"
    copy_from = "missing_item"
    result, value = plugin.measure(ri, name, copy_from)
    assert result == name
    assert value is None


def test_test_fail_me_plugin(self):
    plugin = TestFailMePlugin()
    ri = Mock()
    name = "test_fail"
    with pytest.raises(ZeroDivisionError):
        plugin.measure(ri, name)



def test_config_stuff_string_config(self):
    config = """
    test_var: "{{ env.TEST_VAR }}"
    """
    with patch.dict("os.environ", {"TEST_VAR": "test_value"}), \
         patch("yaml.safe_load") as mock_yaml_load:
        config = config_stuff(config)
        assert config["test_var"] == "test_value"
        mock_yaml_load.assert_called_once()



@patch("os.path.exists")
def test_config_stuff_file_config(self, mock_exists):
    mock_exists.return_value = True
    with open("test_config.yaml", "w") as f:
        f.write("test_var: some_value")
    with open("test_config.yaml", "r") as f:
        config = config_stuff(f)
    assert config["test_var"] == "some_value"



def test_config_stuff_template_rendering(self):
    config = """
    test_var: "{{ 'prefix_' + env.TEST_VAR }}"
    """
    with patch.dict("os.environ", {"TEST_VAR": "value"}), \
         patch("yaml.safe_load") as mock_yaml_load:
        config = config_stuff(config)
        assert config["test_var"] == "prefix_value"



def test_config_stuff_missing_file(self):
    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        config_stuff("nonexistent_file.yaml")



def test_init_with_string_config(self):
    config = """
    test_item:
      name: cpu_usage
      plugin: constant
      value: 50
    """
    requested_info = RequestedInfo(config)
    assert requested_info.config["test_item"]["name"] == "cpu_usage"
    assert requested_info.measurement_plugins["constant"] is not None

def test_init_with_file_config(self):
    with open("test_config.yaml", "w") as f:
        f.write("test_item: ...")
    with open("test_config.yaml", "r") as f:
        requested_info = RequestedInfo(f)
    assert os.path.exists("test_config.yaml")
    os.remove("test_config.yaml")  # Cleanup



def test_register_measurement_plugin(self):
    requested_info = RequestedInfo({})
    requested_info.register_measurement_plugin("test", Mock())
    assert requested_info.measurement_plugins["test"] is not None

def test_register_measurement_plugin_failure(self):
    requested_info = RequestedInfo({})
    with pytest.raises(Exception):
        requested_info.register_measurement_plugin("invalid", None)



def test_get_config(self):
    config = {"test_item": {"name": "cpu_usage"}}
    requested_info = RequestedInfo(config)
    assert requested_info.get_config() == config



def test_iteration_with_constant_plugin(self):
    config = """
    test_item:
      name: cpu_usage
      plugin: constant
      value: 50
    """
    requested_info = RequestedInfo(config)
    item = next(requested_info)
    assert item == ("cpu_usage", 50)

def test_iteration_with_unknown_plugin(self):
    config = {"test_item": {"name": "cpu_usage", "plugin": "invalid"}}
    requested_info = RequestedInfo(config)
    with pytest.raises(Exception):
        next(requested_info)

def test_iteration_with_plugin_failure(self):
    config = """
    test_item:
      name: cpu_usage
      plugin: constant
      value: 50
    """
    requested_info = RequestedInfo(config)
    with patch.object(ConstantPlugin, "measure", side_effect=Exception("error")) as mock_measure:
        item = next(requested_info)
        assert item == (None, None)
        mock_measure.assert_called_once()



def test_missing_start_end_for_monitoring_items(self):
    config = {"test_item": {"name": "cpu_usage", "plugin": "monitoring_query"}}
    with pytest.raises(ValueError):
        RequestedInfo(config)

