#!/usr/bin/env python3
"""Tests for the opl.generators.inventory_ingress module."""

import unittest

from .context import opl


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    def test_counting(self):
        """Generator must expose the requested message count."""
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(count=10)
        self.assertEqual(pg.count, 10)
        self.assertEqual(pg.counter, 0)

    def test_count(self):
        """Generator must produce the requested number of messages then stop."""
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(count=1)
        _, msg = next(pg)
        self.assertIsInstance(msg, dict)
        with self.assertRaises(StopIteration):
            next(pg)

    def test_templates(self):
        """Generator must support the bundled RHSM and yupana templates."""
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(
            count=1, template="inventory_ingress_RHSM_template.json.j2"
        )
        next(pg)
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(
            count=1, template="inventory_ingress_yupana_template.json.j2"
        )
        next(pg)
