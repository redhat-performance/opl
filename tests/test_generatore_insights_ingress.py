#!/usr/bin/env python3

import unittest

from .context import opl


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
        mid, msg = next(pg)
        self.assertIsInstance(msg, dict)
        with self.assertRaises(StopIteration):
            mid, msg = next(pg)

    def test_templates(self):
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(
            count=1, template="inventory_ingress_RHSM_template.json.j2"
        )
        mid, msg = next(pg)
        pg = opl.generators.inventory_ingress.PayloadRHSMGenerator(
            count=1, template="inventory_ingress_yupana_template.json.j2"
        )
        mid, msg = next(pg)
