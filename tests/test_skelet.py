#!/usr/bin/env python3
"""Tests for opl.skelet."""

import argparse
import unittest

from .context import opl

# Test methods and classes are self-documenting via descriptive names.
# pylint: disable=missing-function-docstring, missing-class-docstring


class TestSkelet(unittest.TestCase):
    def test_test_setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--fake_arg", help="Just to catch test file name when calling tests")
        with opl.skelet.test_setup(parser, args=[]) as (args, _status_data):
            self.assertIn("debug", args)
