#!/usr/bin/env python3

import unittest

from .context import opl


class TestDataInvestigator(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest data_investigator.py
    """

    def setUp(self):
        self.di = opl.data_investigator.DataInvestigator()

    def tierDown(self):
        del(self.di)

    def test_empty(self):
        self.assertEqual(len(self.di.data), 0)

    def test_add(self):
        self.di.add('aaa', [1, 2, 3])
        self.di.add('bbb', [4, 5, 6])
        self.assertEqual(len(self.di.data), 2)
        self.assertEqual(self.di.data['aaa'], [1, 2, 3])
        self.assertEqual(self.di.data['bbb'], [4, 5, 6])

    def test_append(self):
        self.di.add('aaa', [1, 2, 3])
        self.di.append('aaa', 10)
        self.assertEqual(len(self.di.data), 1)
        self.assertEqual(self.di.data['aaa'], [1, 2, 3, 10])

    def test_usable(self):
        self.di.add('aaa', [1.0, 1.1, 1.0, 0.9, 1.0])
        self.di.add('bbb', [1, 2, 3, 4, 5])
        self.assertEqual(len(self.di.data), 2)
        self.assertIn('aaa', self.di.usable)
        self.assertNotIn('bbb', self.di.usable)

    def test_usable_extra(self):
        self.di.add('aaa', [1.0, 1.1, 1.0])
        self.di.add('bbb', [1, 2, 3])
        self.assertEqual(len(self.di.data), 2)
        self.assertIn('aaa', self.di.usable)
        self.assertNotIn('bbb', self.di.usable)
        self.di.add('ccc', [10, 10, 10])
        self.assertIn('aaa', self.di.usable)
        self.assertNotIn('bbb', self.di.usable)
        self.assertIn('ccc', self.di.usable)
        for i in range(100, 103):
            self.di.append('aaa', i)
        self.assertNotIn('aaa', self.di.usable)
        self.assertNotIn('bbb', self.di.usable)
        self.assertIn('ccc', self.di.usable)

    def test_check_test_data(self):
        self.di.add('aaa', [1.0, 1.1, 0.9])
        self.assertTrue(self.di.check_test_data({'aaa': 100}))
        self.assertFalse(self.di.check_test_data({'bbb': 100}))

    def test_test_data(self):
        self.di.add('aaa', [1.0, 1.1, 0.9])
        self.assertEqual(self.di.test_data({'aaa': 1}), [])
        self.assertEqual(self.di.test_data({'aaa': 100}), ['aaa'])

    def test_test_data_multiple(self):
        self.di.add('aaa', [1.0, 1.1, 0.9])
        self.assertEqual(self.di.test_data({'aaa': 1, 'bbb': 100}), [])
        self.assertEqual(self.di.test_data({'aaa': 100, 'bbb': 100}), ['aaa'])

    def test_show(self):
        self.di.add('aaa', [1, 2, 3])
        self.assertIn('Processing', self.di.show())
        self.assertIn('aaa', self.di.show())
        self.assertIn('data', self.di.show())

    def test_analyse(self):
        self.di.add('aaa', [1, 2, 3])
        self.assertIn('Processing', self.di.analysis())
        self.assertIn('aaa', self.di.analysis())
        self.assertIn('data', self.di.analysis())
        self.assertIn('Is usable', self.di.analysis())
