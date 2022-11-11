#!/usr/bin/env python3

import yaml
import unittest
import datetime
import tempfile
import os

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
        before = datetime.datetime.utcnow().year
        k, v = next(ri)
        after = datetime.datetime.utcnow().year
        self.assertEqual(k, 'mydate')
        self.assertGreaterEqual(int(v), before)
        self.assertGreaterEqual(after, int(v))

    def test_json(self):
        string = """
            - name: myjson
              command: echo '{"aaa":123,"bbb":456}'
              output: json
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, 'myjson')
        self.assertEqual(v['aaa'], 123)
        self.assertEqual(v['bbb'], 456)

    def test_yaml(self):
        string = """
            - name: myyaml
              command: 'echo -e "aaa: 123\\nbbb: 456"'
              output: yaml
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, 'myyaml')
        self.assertEqual(v['aaa'], 123)
        self.assertEqual(v['bbb'], 456)

    def test_measurements(self):
        class TestMeasurementPlugin(opl.cluster_read.BasePlugin):
            def measure(self, ri, name, test_measurement_query):
                if test_measurement_query == 'simple':
                    return name, opl.data.data_stats([1, 2, 3])

        string = """
            - name: mymeasurement
              test_measurement_query: simple
        """
        ri = opl.cluster_read.RequestedInfo(string)
        ri.register_measurement_plugin('test_measurement_query', TestMeasurementPlugin({}))
        k, v = next(ri)
        self.assertEqual(k, 'mymeasurement')
        self.assertEqual(v['samples'], 3)
        self.assertEqual(v['mean'], 2)

    def test_config_type(self):
        string = """
            - name: mygreet
              command: echo 'hello'
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, 'mygreet')
        self.assertEqual(v, 'hello')
        tmp_file = tempfile.mkstemp()[1]
        with open(tmp_file, 'w') as fpw:
            fpw.write(string)
        with open(tmp_file, 'r') as fpr:
            ri = opl.cluster_read.RequestedInfo(fpr)
            k, v = next(ri)
            self.assertEqual(k, 'mygreet')
            self.assertEqual(v, 'hello')
        os.remove(tmp_file)

    def test_jinja2_config(self):
        string = """
            {% for item in [1, 2] %}
            - name: myenv-{{ item }}
              command: echo '{{ SOMETHING }}-{{ item }}'
            {% endfor %}
        """
        os.environ['SOMETHING'] = 'foobarbaz'
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, 'myenv-1')
        self.assertEqual(v, 'foobarbaz-1')
        k, v = next(ri)
        self.assertEqual(k, 'myenv-2')
        self.assertEqual(v, 'foobarbaz-2')

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
        self.assertEqual(k, 'myconstant')
        self.assertEqual(v, 'Hello world')

    def test_copy_from(self):
        string = """
            - name: somevalue
              constant: Hello world
            - name: mycopyfrom
              copy_from: somevalue
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, 'somevalue')
        self.assertEqual(v, 'Hello world')
        k, v = next(ri)
        self.assertEqual(k, 'mycopyfrom')
        self.assertEqual(v, 'Hello world')

    def test_copy_from_negative(self):
        string = """
            - name: somevalue
              constant: Hello world
            - name: mycopyfrom
              copy_from: somevalue_that_does_not_exist
        """
        ri = opl.cluster_read.RequestedInfo(string)
        k, v = next(ri)
        self.assertEqual(k, 'somevalue')
        self.assertEqual(v, 'Hello world')
        k, v = next(ri)
        self.assertEqual(k, 'mycopyfrom')
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
