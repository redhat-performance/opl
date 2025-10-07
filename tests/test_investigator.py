#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import argparse
import pyfakefs.fake_filesystem_unittest

from .context import opl

SD_NORMAL = """
{
    "started": "2025-10-07T05:18:00+00:00",
    "metric1": 5,
    "metric2": 1000
}
"""

HISTORY_NORMAL = """
metric1,metric2
5,1000
6,995
4,1000
5,1005
"""

CONFIG_NORMAL = """
history:
  type: csv
  file: /tmp/history.csv
current:
  type: status_data
  file: /tmp/status-data.json
sets:
  - metric1
  - metric2
methods:
  - check_by_min_max_0_1
decisions:
  type: csv
  file: /tmp/decisions.csv
"""

CONFIG_METHODS_PARTIAL = """
history:
  type: csv
  file: /tmp/history.csv
current:
  type: status_data
  file: /tmp/status-data.json
sets:
  - name: metric1
    methods:
      - name: check_by_provided_min_max
        args:
          - 4.5
          - 5.5
  - name: metric2
methods:
  - check_by_min_max_0_1
decisions:
  type: csv
  file: /tmp/decisions.csv
"""

class TestInvestigator(pyfakefs.fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def test_happy(self):
        files = {
            "/tmp/status-data.json": SD_NORMAL,
            "/tmp/history.csv": HISTORY_NORMAL,
            "/tmp/investigator_conf.yaml": CONFIG_NORMAL,
        }
        for f, c in files.items():
            with open(f, "w") as fd:
                fd.write(c.strip())

        args = argparse.Namespace()
        args.current_file = None
        args.config = open("/tmp/investigator_conf.yaml", "r")
        args.detailed_decisions = False
        args.stats = False
        args.dry_run = False
        args.debug = True
        rc = opl.pass_or_fail.doit(args)

        # Test overall return code
        self.assertEqual(rc, 0)

        # Test loaded config
        self.assertEqual(args.history_type, "csv")
        self.assertEqual(args.current_type, "status_data")
        self.assertEqual(args.sets, [{'methods': [{'name': 'check_by_min_max_0_1'}], 'name': 'metric1'}, {'methods': [{'name': 'check_by_min_max_0_1'}], 'name': 'metric2'}])
        self.assertEqual(args.methods, ["check_by_min_max_0_1"])
        self.assertEqual(args.decisions_type, "csv")

        # Check recorded decisions
        with open("/tmp/decisions.csv", "r") as fd:
            decisions = fd.readlines()
        self.assertTrue(decisions[1].startswith("metric1,PASS,check_by_min_max_0_1,5,4.0,6.0,,,,"))
        self.assertTrue(decisions[2].startswith("metric2,PASS,check_by_min_max_0_1,1000,995.0,1005.0,,,,"))

    def test_happy_methods_partial(self):
        files = {
            "/tmp/status-data.json": SD_NORMAL,
            "/tmp/history.csv": HISTORY_NORMAL,
            "/tmp/investigator_conf.yaml": CONFIG_METHODS_PARTIAL,
        }
        for f, c in files.items():
            with open(f, "w") as fd:
                fd.write(c.strip())

        args = argparse.Namespace()
        args.current_file = None
        args.config = open("/tmp/investigator_conf.yaml", "r")
        args.detailed_decisions = False
        args.stats = False
        args.dry_run = False
        args.debug = True
        rc = opl.pass_or_fail.doit(args)

        # Test overall return code
        self.assertEqual(rc, 0)

        # Test loaded config
        self.assertEqual(args.history_type, "csv")
        self.assertEqual(args.current_type, "status_data")
        self.assertEqual(args.sets, [
            {'methods': [{'name': 'check_by_provided_min_max', 'args': [4.5, 5.5]}, {'name': 'check_by_min_max_0_1'}], 'name': 'metric1'},
            {'methods': [{'name': 'check_by_min_max_0_1'}], 'name': 'metric2'},
        ])
        self.assertEqual(args.methods, ["check_by_min_max_0_1"])
        self.assertEqual(args.decisions_type, "csv")

        # Check recorded decisions
        with open("/tmp/decisions.csv", "r") as fd:
            decisions = fd.readlines()
        self.assertTrue(decisions[1].startswith("metric1,PASS,check_by_provided_min_max,5,4.5,5.5,,,,"))
        self.assertTrue(decisions[2].startswith("metric1,PASS,check_by_min_max_0_1,5,4.0,6.0,,,,"))
        self.assertTrue(decisions[3].startswith("metric2,PASS,check_by_min_max_0_1,1000,995.0,1005.0,,,,"))
