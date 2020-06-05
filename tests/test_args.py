#!/usr/bin/env python3

import unittest
import argparse

from .context import opl


class TestArgs(unittest.TestCase):

    def test_add_storage_db_opts(self):
        parser = argparse.ArgumentParser()
        opl.args.add_storage_db_opts(parser)
        self.assertIn('--storage-db-host', parser.format_help())
