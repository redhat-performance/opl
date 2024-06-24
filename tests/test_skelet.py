#!/usr/bin/env python3

import unittest
import argparse
import datetime

from .context import opl


class TestSkelet(unittest.TestCase):
    def test_test_setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--fake_arg", help="Just to catch test file name when calling tests"
        )
        with opl.skelet.test_setup(parser) as (args, status_data):
            self.assertIn("debug", args)
