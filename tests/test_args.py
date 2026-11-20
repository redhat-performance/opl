#!/usr/bin/env python3
"""Tests for opl.args."""

import argparse
import unittest

from .context import opl

# Test methods and classes are self-documenting via descriptive names.
# pylint: disable=missing-function-docstring, missing-class-docstring


class TestArgs(unittest.TestCase):
    def test_add_storage_db_opts(self):
        parser = argparse.ArgumentParser()
        opl.args.add_storage_db_opts(parser)
        self.assertIn("--storage-db-host", parser.format_help())
