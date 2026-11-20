#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tests for the opl.investigator and opl.pass_or_fail modules."""

import argparse
import unittest

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
    """End-to-end investigator tests on a fake filesystem."""

    def setUp(self):
        """Set up the fake filesystem."""
        self.setUpPyfakefs()

    def test_happy(self):
        """Full run with a valid config must pass and record decisions."""
        files = {
            "/tmp/status-data.json": SD_NORMAL,
            "/tmp/history.csv": HISTORY_NORMAL,
            "/tmp/investigator_conf.yaml": CONFIG_NORMAL,
        }
        for f, c in files.items():
            with open(f, "w", encoding="utf-8") as fd:
                fd.write(c.strip())

        args = argparse.Namespace()
        args.current_file = None
        args.config = open(  # pylint: disable=consider-using-with  # ownership handed to the code under test
            "/tmp/investigator_conf.yaml", "r", encoding="utf-8"
        )
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
        self.assertEqual(
            args.sets,
            [
                {"methods": [{"name": "check_by_min_max_0_1"}], "name": "metric1"},
                {"methods": [{"name": "check_by_min_max_0_1"}], "name": "metric2"},
            ],
        )
        self.assertEqual(args.methods, ["check_by_min_max_0_1"])
        self.assertEqual(args.decisions_type, "csv")

        # Check recorded decisions
        with open("/tmp/decisions.csv", "r", encoding="utf-8") as fd:
            decisions = fd.readlines()
        self.assertTrue(
            decisions[1].startswith("metric1,PASS,check_by_min_max_0_1,5,4.0,6.0,,,,")
        )
        self.assertTrue(
            decisions[2].startswith(
                "metric2,PASS,check_by_min_max_0_1,1000,995.0,1005.0,,,,"
            )
        )

    def test_happy_methods_partial(self):
        """Run with methods applying only to some metrics must still pass."""
        files = {
            "/tmp/status-data.json": SD_NORMAL,
            "/tmp/history.csv": HISTORY_NORMAL,
            "/tmp/investigator_conf.yaml": CONFIG_METHODS_PARTIAL,
        }
        for f, c in files.items():
            with open(f, "w", encoding="utf-8") as fd:
                fd.write(c.strip())

        args = argparse.Namespace()
        args.current_file = None
        args.config = open(  # pylint: disable=consider-using-with  # ownership handed to the code under test
            "/tmp/investigator_conf.yaml", "r", encoding="utf-8"
        )
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
        self.assertEqual(
            args.sets,
            [
                {
                    "methods": [
                        {"name": "check_by_provided_min_max", "args": [4.5, 5.5]},
                        {"name": "check_by_min_max_0_1"},
                    ],
                    "name": "metric1",
                },
                {"methods": [{"name": "check_by_min_max_0_1"}], "name": "metric2"},
            ],
        )
        self.assertEqual(args.methods, ["check_by_min_max_0_1"])
        self.assertEqual(args.decisions_type, "csv")

        # Check recorded decisions
        with open("/tmp/decisions.csv", "r", encoding="utf-8") as fd:
            decisions = fd.readlines()
        self.assertTrue(
            decisions[1].startswith(
                "metric1,PASS,check_by_provided_min_max,5,4.5,5.5,,,,"
            )
        )
        self.assertTrue(
            decisions[2].startswith("metric1,PASS,check_by_min_max_0_1,5,4.0,6.0,,,,")
        )
        self.assertTrue(
            decisions[3].startswith(
                "metric2,PASS,check_by_min_max_0_1,1000,995.0,1005.0,,,,"
            )
        )


class TestCheckIsZero(unittest.TestCase):
    """Tests for the check_is_zero() method."""

    def test_pass_when_zero(self):
        """check_is_zero() must pass for zero."""
        result, info = opl.investigator.check.check_is_zero([], 0)
        self.assertTrue(result)
        self.assertEqual(info["lower_boundary"], 0)
        self.assertEqual(info["upper_boundary"], 0)

    def test_fail_when_positive(self):
        """check_is_zero() must fail for a positive value."""
        result, _ = opl.investigator.check.check_is_zero([], 1)
        self.assertFalse(result)

    def test_fail_when_negative(self):
        """check_is_zero() must fail for a negative value."""
        result, _ = opl.investigator.check.check_is_zero([], -1)
        self.assertFalse(result)
