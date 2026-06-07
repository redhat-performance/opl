#!/usr/bin/env python3

import yaml
import unittest
import tempfile
import os
import argparse
import datetime
from urllib.parse import parse_qs, urlparse

import responses

from .context import opl


class TestRequestedInfo(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest cluster_read.py
    """

    def test_date(self):
        string = """
            - name: mydate
              command: date --utc +%Y
        """
        ri = opl.cluster_read.RequestedInfo(string)
        before = opl.date.get_now().year
        k, v = next(ri)
        after = opl.date.get_now().year
        self.assertEqual(k, "mydate")
        self.assertGreaterEqual(int(v), before)
        self.assertGreaterEqual(after, int(v))

    def test_count(self):
        string = """
            - name: print.output
              log_source_command: echo -e "error line1\\ninfo line2\\nwarning line3\\nerror line4"
              log_regexp_error: '^error '
              log_regexp_warning: '^warning '
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "print.output")
        self.assertEqual(v, {"all": 4, "error": 2, "warning": 1})

    def test_count_large(self):
        string = """
            - name: print.output
              log_source_command: echo -e '{"level":"error", "logger":"ABC", "msg":"Oh no"}\\n{"level":"info", "logger":"XYZ", "msg":"Hello!"}\\n{"level":"error", "logger":"XYZ", "msg":"Oh no"}\\n{"level":"warning", "logger":"XYZ", "msg":"Beware"}',
              log_regexp_error_abc: '"level":"error", "logger":"ABC"'
              log_regexp_error_xyz: '"level":"error", "logger":"XYZ"'
              log_regexp_warning: '"level":"warning"'
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "print.output")
        self.assertEqual(v, {"all": 4, "error_abc": 1, "error_xyz": 1, "warning": 1})

    def test_json(self):
        string = """
            - name: myjson
              command: echo '{"aaa":123,"bbb":456}'
              output: json
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "myjson")
        self.assertEqual(v["aaa"], 123)
        self.assertEqual(v["bbb"], 456)

    def test_yaml(self):
        string = """
            - name: myyaml
              command: 'echo -e "aaa: 123\\nbbb: 456"'
              output: yaml
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "myyaml")
        self.assertEqual(v["aaa"], 123)
        self.assertEqual(v["bbb"], 456)

    def test_measurements(self):
        class TestMeasurementPlugin(opl.cluster_read.BasePlugin):
            def measure(self, ri, name, test_measurement_query):
                if test_measurement_query == "simple":
                    return name, opl.data.data_stats([1, 2, 3])

        string = """
            - name: mymeasurement
              test_measurement_query: simple
        """
        ri = opl.cluster_read.RequestedInfo(string)
        ri.register_measurement_plugin(
            "test_measurement_query", TestMeasurementPlugin({})
        )
        k, v = next(ri)
        self.assertEqual(k, "mymeasurement")
        self.assertEqual(v["samples"], 3)
        self.assertEqual(v["mean"], 2)

    def test_config_type(self):
        string = """
            - name: mygreet
              command: echo 'hello'
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "mygreet")
        self.assertEqual(v, "hello")
        tmp_file = tempfile.mkstemp()[1]
        with open(tmp_file, "w") as fpw:
            fpw.write(string)
        with open(tmp_file, "r") as fpr:
            ri = opl.cluster_read.RequestedInfo(fpr)
            k, v = next(ri)
            self.assertEqual(k, "mygreet")
            self.assertEqual(v, "hello")
        os.remove(tmp_file)

    def test_jinja2_config(self):
        string = """
            {% for item in [1, 2] %}
            - name: myenv-{{ item }}
              command: echo '{{ SOMETHING }}-{{ item }}'
            {% endfor %}
        """
        os.environ["SOMETHING"] = "foobarbaz"
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "myenv-1")
        self.assertEqual(v, "foobarbaz-1")
        k, v = next(ri)
        self.assertEqual(k, "myenv-2")
        self.assertEqual(v, "foobarbaz-2")

    def test_get_config(self):
        string = """
            - name: mygreet
              command: echo 'hello'
        """
        ri = opl.cluster_read.RequestedInfo(string)
        orig = yaml.load(string, Loader=yaml.SafeLoader)
        self.assertEqual(orig, ri.get_config())

    def test_constant(self):
        string = """
            - name: myconstant
              constant: Hello world
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, "myconstant")
        self.assertEqual(v, "Hello world")

    def test_copy_from(self):
        string = """
            - name: somevalue
              constant: Hello world
            - name: mycopyfrom_exists
              copy_from: somevalue
            - name: mycopyfrom_missing
              copy_from: somevalue_that_does_not_exist
        """
        sd = opl.status_data.StatusData(tempfile.NamedTemporaryFile().name)
        ri = opl.cluster_read.RequestedInfo(string, sd=sd)
        k, v = next(ri)
        self.assertEqual(k, "somevalue")
        self.assertEqual(v, "Hello world")
        sd.set(k, v)

        k, v = next(ri)
        self.assertEqual(k, "mycopyfrom_exists")
        self.assertEqual(v, "Hello world")
        k, v = next(ri)
        self.assertEqual(k, "mycopyfrom_missing")
        self.assertEqual(v, None)

    def test_copy_from_previous(self):
        string = """
            - name: somevalue
              constant: Hello world
        """
        ri = opl.cluster_read.RequestedInfo(string)
        sd = opl.status_data.StatusData(tempfile.NamedTemporaryFile().name)
        k, v = next(ri)
        sd.set(k, v)

        string = """
            - name: mycopyfrom_exists
              copy_from: somevalue
            - name: mycopyfrom_missing
              copy_from: somevalue_that_does_not_exist
        """
        ri = opl.cluster_read.RequestedInfo(string, sd=sd)
        k, v = next(ri)
        self.assertEqual(k, "mycopyfrom_exists")
        self.assertEqual(v, "Hello world")
        k, v = next(ri)
        self.assertEqual(k, "mycopyfrom_missing")
        self.assertEqual(v, None)

    def test_wrong_config(self):
        """If plugin throws an exception, (None, None) should be returned"""
        string = """
            - name: some_name
              test_fail_me: abc
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, None)
        self.assertEqual(v, None)


class TestGrafanaPlugin(unittest.TestCase):

    mock_post_get_load_simple = {
        "mock": {
            "method": responses.POST,
            "url": "http://grafana.example.com:443/api/datasources/proxy/42/render",
            "json": [
                {
                    "target": "someprefix.node001_example_com.load.load.shortterm",
                    "datapoints": [
                        [10.0, 1740787205],
                        [15.0, 1740787220],
                        [5.0, 1740787235],
                        [10.0, 1740787250],
                    ],
                }
            ],
            "status": 200,
        },
        "args": argparse.Namespace(
            grafana_host="http://grafana.example.com",
            grafana_port=443,
            grafana_prefix="someprefix",
            grafana_datasource=42,
            grafana_interface="interface-enp2s0",
            grafana_token="secret",
            grafana_node="node001_example_com",
        ),
        "start": datetime.datetime.fromisoformat("2025-03-01T00:00:00+00:00"),
        "end": datetime.datetime.fromisoformat("2025-03-01T00:01:00+00:00"),
    }

    @responses.activate
    def test_basic(self):
        # Configure mock
        responses.add(
            **self.mock_post_get_load_simple["mock"],
        )

        # Configure the request we are going to make
        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
        """

        # Actual test using the mock
        ri = opl.cluster_read.RequestedInfo(
            string,
            start=self.mock_post_get_load_simple["start"],
            end=self.mock_post_get_load_simple["end"],
            args=self.mock_post_get_load_simple["args"],
        )
        k, v = next(ri)
        self.assertEqual(k, "measurement.load")
        self.assertEqual(int(v["min"]), 5)
        self.assertEqual(int(v["mean"]), 10)
        self.assertEqual(int(v["median"]), 10)
        self.assertEqual(int(v["max"]), 15)
        self.assertEqual(int(v["samples"]), 4)
        self.assertNotIn("variables", v)
        self.assertNotIn("enritchment", v)

    @responses.activate
    def test_added_variables(self):
        # Configure mock
        responses.add(
            **self.mock_post_get_load_simple["mock"],
        )

        # Configure the request we are going to make
        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
              grafana_include_vars: true
        """

        # Actual test using the mock
        ri = opl.cluster_read.RequestedInfo(
            string,
            start=self.mock_post_get_load_simple["start"],
            end=self.mock_post_get_load_simple["end"],
            args=self.mock_post_get_load_simple["args"],
        )
        k, v = next(ri)
        self.assertEqual(k, "measurement.load")
        self.assertEqual(int(v["mean"]), 10)
        self.assertEqual(v["variables"]["$Node"], "node001_example_com")
        self.assertEqual(v["variables"]["$Interface"], "interface-enp2s0")
        self.assertEqual(v["variables"]["$Cloud"], "someprefix")
        self.assertNotIn("enritchment", v)

    @responses.activate
    def test_added_enritchment(self):
        # Configure mock
        responses.add(
            **self.mock_post_get_load_simple["mock"],
        )

        # Configure the request we are going to make
        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
              grafana_enritchment:
                hello: world
                answer: 42
        """

        # Actual test using the mock
        ri = opl.cluster_read.RequestedInfo(
            string,
            start=self.mock_post_get_load_simple["start"],
            end=self.mock_post_get_load_simple["end"],
            args=self.mock_post_get_load_simple["args"],
        )
        k, v = next(ri)
        self.assertEqual(k, "measurement.load")
        self.assertEqual(int(v["mean"]), 10)
        self.assertEqual(v["enritchment"]["hello"], "world")
        self.assertEqual(v["enritchment"]["answer"], 42)
        self.assertNotIn("variables", v)

    mock_post_get_batch = {
        "mock": {
            "method": responses.POST,
            "url": "http://grafana.example.com:443/api/datasources/proxy/42/render",
            "json": [
                {
                    "target": "someprefix.node001_example_com.load.load.shortterm",
                    "datapoints": [[10.0, 1740787205], [15.0, 1740787220]],
                },
                {
                    "target": "someprefix.node001_example_com.memory.memory-used",
                    "datapoints": [[1000.0, 1740787205], [2000.0, 1740787220]],
                },
                {
                    "target": "someprefix.node001_example_com.swap.swap-used",
                    "datapoints": [[100.0, 1740787205], [200.0, 1740787220]],
                },
            ],
            "status": 200,
        },
        "args": argparse.Namespace(
            grafana_host="http://grafana.example.com",
            grafana_port=443,
            grafana_prefix="someprefix",
            grafana_datasource=42,
            grafana_interface="interface-enp2s0",
            grafana_token="secret",
            grafana_node="node001_example_com",
            grafana_chunk_size=10,
        ),
        "start": datetime.datetime.fromisoformat("2025-03-01T00:00:00+00:00"),
        "end": datetime.datetime.fromisoformat("2025-03-01T00:01:00+00:00"),
    }

    @responses.activate
    def test_batch_consecutive_targets(self):
        """Consecutive Grafana items are batched into one HTTP request."""
        responses.add(**self.mock_post_get_batch["mock"])

        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
            - name: measurement.memory
              grafana_target: $Cloud.$Node.memory.memory-used
            - name: measurement.swap
              grafana_target: $Cloud.$Node.swap.swap-used
        """

        ri = opl.cluster_read.RequestedInfo(
            string,
            start=self.mock_post_get_batch["start"],
            end=self.mock_post_get_batch["end"],
            args=self.mock_post_get_batch["args"],
        )
        results = list(ri)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "measurement.load")
        self.assertEqual(int(results[0][1]["mean"]), 12)
        self.assertEqual(results[1][0], "measurement.memory")
        self.assertEqual(int(results[1][1]["mean"]), 1500)
        self.assertEqual(results[2][0], "measurement.swap")
        self.assertEqual(int(results[2][1]["mean"]), 150)
        # Only one HTTP request should have been made
        self.assertEqual(len(responses.calls), 1)
        # All parameters must be in POST body, not query string
        req = responses.calls[0].request
        self.assertEqual(urlparse(req.url).query, "")
        body = parse_qs(req.body)
        self.assertEqual(len(body["target"]), 3)
        self.assertIn("from", body)
        self.assertIn("until", body)
        self.assertIn("format", body)

    @responses.activate
    def test_batch_fallback_on_failure(self):
        """On batch failure, falls back to individual measure() calls."""
        # First call (batch) fails, next 3 individual calls succeed
        responses.add(
            method=responses.POST,
            url="http://grafana.example.com:443/api/datasources/proxy/42/render",
            json={"error": "server error"},
            status=500,
        )
        for target_data in self.mock_post_get_batch["mock"]["json"]:
            responses.add(
                method=responses.POST,
                url="http://grafana.example.com:443/api/datasources/proxy/42/render",
                json=[target_data],
                status=200,
            )

        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
            - name: measurement.memory
              grafana_target: $Cloud.$Node.memory.memory-used
            - name: measurement.swap
              grafana_target: $Cloud.$Node.swap.swap-used
        """

        ri = opl.cluster_read.RequestedInfo(
            string,
            start=self.mock_post_get_batch["start"],
            end=self.mock_post_get_batch["end"],
            args=self.mock_post_get_batch["args"],
        )
        results = list(ri)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "measurement.load")
        self.assertEqual(int(results[0][1]["mean"]), 12)
        self.assertEqual(results[1][0], "measurement.memory")
        self.assertEqual(int(results[1][1]["mean"]), 1500)
        self.assertEqual(results[2][0], "measurement.swap")
        self.assertEqual(int(results[2][1]["mean"]), 150)

    @responses.activate
    def test_batch_boundary_at_non_grafana_item(self):
        """Non-Grafana items between Grafana items create batch boundaries."""
        # Two separate batch requests expected
        responses.add(
            method=responses.POST,
            url="http://grafana.example.com:443/api/datasources/proxy/42/render",
            json=[self.mock_post_get_batch["mock"]["json"][0]],
            status=200,
        )
        responses.add(
            method=responses.POST,
            url="http://grafana.example.com:443/api/datasources/proxy/42/render",
            json=[self.mock_post_get_batch["mock"]["json"][2]],
            status=200,
        )

        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
            - name: measurement.group
              constant: mygroup
            - name: measurement.swap
              grafana_target: $Cloud.$Node.swap.swap-used
        """

        ri = opl.cluster_read.RequestedInfo(
            string,
            start=self.mock_post_get_batch["start"],
            end=self.mock_post_get_batch["end"],
            args=self.mock_post_get_batch["args"],
        )
        results = list(ri)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "measurement.load")
        self.assertEqual(results[1][0], "measurement.group")
        self.assertEqual(results[1][1], "mygroup")
        self.assertEqual(results[2][0], "measurement.swap")
        # Two HTTP requests (two batches, split by constant)
        self.assertEqual(len(responses.calls), 2)

    @responses.activate
    def test_batch_output_matches_individual_output(self):
        """Batched output must be identical to single-item output."""
        string = """
            - name: measurement.load
              grafana_target: $Cloud.$Node.load.load.shortterm
            - name: measurement.memory
              grafana_target: $Cloud.$Node.memory.memory-used
            - name: measurement.swap
              grafana_target: $Cloud.$Node.swap.swap-used
        """

        # Run with chunk_size=1 (individual requests, old behavior)
        for target_data in self.mock_post_get_batch["mock"]["json"]:
            responses.add(
                method=responses.POST,
                url="http://grafana.example.com:443/api/datasources/proxy/42/render",
                json=[target_data],
                status=200,
            )

        args_single = argparse.Namespace(
            **{**vars(self.mock_post_get_batch["args"]), "grafana_chunk_size": 1}
        )
        single = list(
            opl.cluster_read.RequestedInfo(
                string,
                start=self.mock_post_get_batch["start"],
                end=self.mock_post_get_batch["end"],
                args=args_single,
            )
        )

        # Run with chunk_size=50 (batched, new behavior)
        responses.add(**self.mock_post_get_batch["mock"])

        args_batched = argparse.Namespace(
            **{**vars(self.mock_post_get_batch["args"]), "grafana_chunk_size": 50}
        )
        batched = list(
            opl.cluster_read.RequestedInfo(
                string,
                start=self.mock_post_get_batch["start"],
                end=self.mock_post_get_batch["end"],
                args=args_batched,
            )
        )

        self.assertEqual(single, batched)
