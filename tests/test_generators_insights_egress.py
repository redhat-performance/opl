#!/usr/bin/env python3
"""Tests for the opl.generators.inventory_egress module."""

import unittest

from .context import opl


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    def test_counting(self):
        """Generator must expose count, package count and message type."""
        pg = opl.generators.inventory_egress.EgressHostsGenerator(
            count=3, n_packages=10, msg_type="created"
        )
        self.assertEqual(pg.count, 3)
        self.assertEqual(pg.n_packages, 10)
        self.assertEqual(pg.msg_type, "created")

    def test_count(self):
        """Generator must produce one message then stop."""
        pg = opl.generators.inventory_egress.EgressHostsGenerator()
        next(pg)
        with self.assertRaises(StopIteration):
            next(pg)

    def test_type(self):
        """Generated message must be a dict."""
        pg = opl.generators.inventory_egress.EgressHostsGenerator()
        _, msg = next(pg)
        self.assertIsInstance(msg, dict)
