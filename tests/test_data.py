#!/usr/bin/env python3

import datetime
import unittest

from .context import opl


class TestSkelet(unittest.TestCase):

    def test_data_stats(self):
        stats = opl.data.data_stats([0, 1, 1, 2, 2, 1, 1, 0])
        self.assertEqual(stats['samples'], 8)
        self.assertEqual(stats['min'], 0)
        self.assertEqual(stats['mean'], 1)
        self.assertEqual(stats['max'], 2)
        self.assertEqual(stats['range'], 2)
        self.assertEqual(stats['percentile25'], 0.75)
        self.assertEqual(stats['percentile75'], 1.25)
        self.assertEqual(stats['iqr'], 0.5)

    def test_data_stats_empty(self):
        stats = opl.data.data_stats([])
        self.assertEqual(stats['samples'], 0)
        self.assertEqual(len(stats), 1)

    def test_data_stats_short(self):
        stats = opl.data.data_stats([1])
        self.assertEqual(stats['samples'], 1)
        self.assertEqual(stats['stdev'], 0.0)

    def test_data_stats_datetime(self):
        data = [
            datetime.datetime.fromisoformat('2021-03-22T12:00:00.000000+00:00'),
            datetime.datetime.fromisoformat('2021-03-22T11:50:00.000000+00:00'),
            datetime.datetime.fromisoformat('2021-03-22T11:30:00.000000+00:00'),
            datetime.datetime.fromisoformat('2021-03-22T11:00:00.000000+00:00'),
        ]
        stats = opl.data.data_stats(data)
        self.assertEqual(stats['samples'], 4)
        self.assertEqual(stats['max'], datetime.datetime.fromisoformat('2021-03-22T12:00:00.000000+00:00'))
        self.assertEqual(stats['min'], datetime.datetime.fromisoformat('2021-03-22T11:00:00.000000+00:00'))
        self.assertEqual(stats['range'].total_seconds(), 3600)

    def test_get_hist(self):
        hist = opl.data.get_hist([0, 1, 1, 2, 2, 1, 1, 0])
        self.assertEqual(
            hist,
            [
                ((0.0, 0.2), 2.0),
                ((0.2, 0.4), 0.0),
                ((0.4, 0.6000000000000001), 0.0),
                ((0.6000000000000001, 0.8), 0.0),
                ((0.8, 1.0), 0.0),
                ((1.0, 1.2000000000000002), 4.0),
                ((1.2000000000000002, 1.4000000000000001), 0.0),
                ((1.4000000000000001, 1.6), 0.0),
                ((1.6, 1.8), 0.0),
                ((1.8, 2.0), 2.0),
            ],
        )

    def test_get_rps(self):
        rps_vals = opl.data.get_rps([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], bucket_size=10, granularity=1)
        self.assertEqual(len(rps_vals), 10)
        self.assertEqual(sum(rps_vals)/len(rps_vals), 1.0)

        rps_vals = opl.data.get_rps([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(len(rps_vals), 5)
        self.assertEqual(sum(rps_vals)/len(rps_vals), 1.0)
