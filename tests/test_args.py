#!/usr/bin/env python3
"""Tests for the opl.args module."""

import argparse
import unittest

from .context import opl


class TestArgs(unittest.TestCase):
    """Tests for CLI option helpers in opl.args."""

    def test_add_storage_db_opts(self):
        """add_storage_db_opts() must add storage DB options to the parser."""
        parser = argparse.ArgumentParser()
        opl.args.add_storage_db_opts(parser)
        self.assertIn("--storage-db-host", parser.format_help())
