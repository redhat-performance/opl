#!/usr/bin/env python3

import csv
import json
import os
import sys
import tempfile
import unittest
import unittest.mock

from .context import opl  # noqa: F401

import opl.pass_or_fail  # noqa: E402


class TestPassOrFail(unittest.TestCase):

    def test_error_decision_names_the_data_set_and_the_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = os.path.join(tmp, "history.csv")
            with open(history, "w") as fp:
                fp.write("a,b\n1,10\n2,20\n3,30\n")
            current = os.path.join(tmp, "current.json")
            with open(current, "w") as fp:
                json.dump({"a": 2}, fp)  # no "b": its check can not run
            decisions = os.path.join(tmp, "decisions.csv")
            config = os.path.join(tmp, "config.yaml")
            with open(config, "w") as fp:
                fp.write(
                    f"history:\n  type: csv\n  file: {history}\n"
                    f"current:\n  type: status_data\n  file: {current}\n"
                    "methods: [check_by_min_max_0_1]\n"
                    "sets: [a, b]\n"
                    f"decisions:\n  type: csv\n  filename: {decisions}\n"
                )

            with unittest.mock.patch.object(
                sys, "argv", ["pass_or_fail.py", "--config", config]
            ):
                with self.assertRaises(SystemExit) as raised:
                    opl.pass_or_fail.main()

            exit_code = raised.exception.code

            with open(decisions) as fp:
                rows = {r["description"]: r for r in csv.DictReader(fp)}

        self.assertEqual(exit_code, 2)
        self.assertEqual(rows["a"]["result"], "PASS")
        self.assertEqual(rows["b"]["result"], "ERROR")
        self.assertTrue(rows["b"]["exception"])
