#!/usr/bin/env python3
"""Tests for the opl.generators.qpc_tarball module."""

import os
import unittest

from .context import opl


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    tarball_conf = {
        "tarballs_count": 2,
        "slices_count": 3,
        "hosts_count": 4,
        "hosts_template": "inventory_ingress_yupana_template.json.j2",
        "hosts_packages": 10,
    }

    def test_counting(self):
        """Generator must expose the requested tarball count."""
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(
            count=2, tarball_conf=self.tarball_conf
        )
        self.assertEqual(pg.count, 2)
        self.assertEqual(pg.counter, 0)

    def test_count(self):
        """Generator must produce the requested number of tarballs then stop."""
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(
            count=2, tarball_conf=self.tarball_conf
        )
        tarball = next(pg)
        self.assertIsInstance(tarball, opl.generators.qpc_tarball.QPCTarball)
        tarball = next(pg)
        with self.assertRaises(StopIteration):
            tarball = next(pg)

    def test_count_slices(self):
        """Tarball must yield the configured number of slices then stop."""
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(
            count=2, tarball_conf=self.tarball_conf
        )
        tarball = next(pg)
        tarball_slice = next(tarball)
        self.assertIsInstance(tarball_slice, opl.generators.qpc_tarball.QPCTarballSlice)
        tarball_slice = next(tarball)
        tarball_slice = next(tarball)
        with self.assertRaises(StopIteration):
            tarball_slice = next(tarball)

    def test_add_hosts(self):
        """add_host() must increase the slice host count."""
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(
            count=2, tarball_conf=self.tarball_conf
        )
        tarball = next(pg)
        tarball_slice = next(tarball)
        for i in range(4):
            tarball_slice.add_host({"fqdn": f"host{i}.example.com"})
        self.assertEqual(tarball_slice.get_host_count(), 4)

    def test_slice_after_dump(self):
        """Dumped slice must keep host count; cleanup must remove files."""
        pg = opl.generators.qpc_tarball.QPCTarballGenerator(
            count=2, tarball_conf=self.tarball_conf
        )
        tarball = next(pg)
        tarball_dirname = tarball.dirname
        tarball_slice = next(tarball)
        for i in range(4):
            tarball_slice.add_host({"fqdn": f"host{i}.example.com"})
        self.assertEqual(tarball_slice.get_host_count(), 4)
        tarball_slice_filename = tarball_slice.dump(tarball.dirname)
        self.assertTrue(os.path.isfile(tarball_slice_filename))
        self.assertEqual(tarball_slice.get_host_count(), 4)
        tarball.cleanup()
        self.assertFalse(os.path.isdir(tarball_dirname.name))
        self.assertFalse(os.path.isfile(tarball_slice_filename))
