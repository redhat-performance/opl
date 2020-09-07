#!/usr/bin/env python3

import unittest

from .context import opl


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    def test_counting(self):
        pg = opl.generators.inventory_egress.EgressHostsGenerator(
            expected=1,
            n_packages=10,
            msg_type='created')
        self.assertEqual(pg.expected, 1)
        self.assertEqual(pg.generated, 0)
        self.assertEqual(pg.n_packages, 10)
        self.assertEqual(pg.msg_type, 'created')

    def test_count(self):
        pg = opl.generators.inventory_egress.EgressHostsGenerator(
            expected=1,
            n_packages=10,
            msg_type='created')
        mid, msg = next(pg)
        self.assertIsInstance(msg, str)
        with self.assertRaises(StopIteration):
            mid, msg = next(pg)
