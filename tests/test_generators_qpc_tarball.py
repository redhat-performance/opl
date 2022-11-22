#!/usr/bin/env python3

import unittest

from .context import opl


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    tarball_conf = {
        'tarballs_count': 2,
        'slices_count': 3,
        'hosts_count': 4,
        'hosts_template': "inventory_ingress_yupana_template.json.j2",
        'hosts_packages': 10,
    }

    def test_counting(self):
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(count=2, tarball_conf=self.tarball_conf)
        self.assertEqual(pg.count, 2)
        self.assertEqual(pg.counter, 0)

    def test_count(self):
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(count=2, tarball_conf=self.tarball_conf)
        tarball = next(pg)
        self.assertIsInstance(tarball, opl.generators.qpc_tarball.QPCTarball)
        tarball = next(pg)
        with self.assertRaises(StopIteration):
            tarball = next(pg)

    def test_count_slices(self):
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(count=2, tarball_conf=self.tarball_conf)
        tarball = next(pg)
        tarball_slice = next(tarball)
        self.assertIsInstance(tarball_slice, opl.generators.qpc_tarball.QPCTarballSlice)
        tarball_slice = next(tarball)
        tarball_slice = next(tarball)
        with self.assertRaises(StopIteration):
            tarball_slice = next(tarball)
