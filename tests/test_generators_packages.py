#!/usr/bin/env python3
"""Tests for opl.generators.packages."""

import unittest

from .context import opl

# Test methods and classes are self-documenting via descriptive names.
# pylint: disable=missing-function-docstring, missing-class-docstring


class TestPayloadGenerator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest script-generate.py
    """

    def test_count(self):
        pg = opl.generators.packages.PackagesGenerator()
        self.assertIsInstance(pg.count(), int)

    def test_counting(self):
        pg = opl.generators.packages.PackagesGenerator()
        self.assertEqual(len(pg.generate(10)), 10)
        self.assertEqual(len(pg.generate(100)), 100)

    def test_looks_like_package_name(self):
        pg = opl.generators.packages.PackagesGenerator()
        for p in pg.generate(10):
            self.assertIsInstance(p, str)
            self.assertTrue(p.endswith("x86_64") or p.endswith("i686") or p.endswith("noarch"))
            self.assertTrue(" " not in p)
            self.assertGreater(len(p), 9)  # minimum is 'a-1.noarch' I think
