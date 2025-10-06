#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import argparse
import unittest.mock

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


# https://stackoverflow.com/questions/26783678/python-mock-builtin-open-in-a-class-using-two-different-files
def get_mock_open(files: dict[str, str]):
    def my_mock_open(filename, *args, **kwargs):
        if filename in files:
            m = unittest.mock.mock_open(read_data=files[filename].strip()).return_value
            m.name = filename
            return m
        raise FileNotFoundError(f"(mock) Unable to open {filename}")
    return unittest.mock.MagicMock(side_effect=my_mock_open)


class TestInvestigator(unittest.TestCase):

    def test_happy(self):
        files = {
            "/tmp/status-data.json": SD_NORMAL,
            "/tmp/history.csv": HISTORY_NORMAL,
            "/tmp/investigator_conf.yaml": CONFIG_NORMAL,
        }
        with unittest.mock.patch('builtins.open', get_mock_open(files)) as m:
            args = argparse.Namespace()
            args.current_file = None
            args.config = open("/tmp/investigator_conf.yaml", "r")
            args.detailed_decisions = False
            args.stats = False
            args.dry_run = True
            args.debug = True
            opl.pass_or_fail.doit(args)

            # Test loaded config
            self.assertEqual(args.history_type, "csv")
            self.assertEqual(args.current_type, "status_data")
            self.assertEqual(args.sets, ["metric1", "metric2"])
            self.assertEqual(args.methods, ["check_by_min_max_0_1"])
            self.assertEqual(args.decisions_type, "csv")
