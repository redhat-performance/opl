#!/usr/bin/env python3
"""Tests for the opl.skelet module."""

import argparse
import unittest

from .context import opl


class TestSkelet(unittest.TestCase):
    """Tests for test_setup()."""

    def test_test_setup(self):
        """test_setup() must return parsed args and a StatusData object."""
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--fake_arg", help="Just to catch test file name when calling tests"
        )
        with opl.skelet.test_setup(parser, args=[]) as (args, _):
            self.assertIn("debug", args)
