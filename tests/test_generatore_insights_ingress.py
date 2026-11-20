#!/usr/bin/env python3
"""Tests for opl.generators.inventory_ingress."""

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
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(count=10)
        self.assertEqual(pg.count, 10)
        self.assertEqual(pg.counter, 0)

    def test_count(self):
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(count=1)
        _mid, msg = next(pg)
        self.assertIsInstance(msg, dict)
        with self.assertRaises(StopIteration):
            next(pg)

    def test_templates(self):
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(
            count=1, template="inventory_ingress_RHSM_template.json.j2"
        )
        next(pg)
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(
            count=1, template="inventory_ingress_yupana_template.json.j2"
        )
        next(pg)
