#!/usr/bin/env python3

import unittest

from .context import opl


class TestSkelet(unittest.TestCase):

    def test_data_stats(self):
        stats = opl.data.data_stats([0, 1, 2, 2, 1, 0])
        self.assertEqual(stats['samples'], 6)
        self.assertEqual(stats['min'], 0)
        self.assertEqual(stats['mean'], 1)
        self.assertEqual(stats['max'], 2)

    def test_get_rps(self):
        rps_vals = opl.data.get_rps([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(len(rps_vals), 10)
        self.assertEqual(sum(rps_vals), 10)
