#!/usr/bin/env python3
"""Tests for opl.generators.inventory_egress."""

import unittest

from .context import opl

# Test methods and classes are self-documenting via descriptive names.
# pylint: disable=missing-function-docstring, missing-class-docstring


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    def test_counting(self):
        pg = opl.generators.inventory_egress.EgressHostsGenerator(count=3, n_packages=10, msg_type="created")
        self.assertEqual(pg.count, 3)
        self.assertEqual(pg.n_packages, 10)
        self.assertEqual(pg.msg_type, "created")

    def test_count(self):
        pg = opl.generators.inventory_egress.EgressHostsGenerator()
        next(pg)
        with self.assertRaises(StopIteration):
            next(pg)

    def test_type(self):
        pg = opl.generators.inventory_egress.EgressHostsGenerator()
        _mid, msg = next(pg)
        self.assertIsInstance(msg, dict)
