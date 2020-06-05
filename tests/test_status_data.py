#!/usr/bin/env python3

import datetime
import os
import unittest
import tempfile

from .context import opl


class TestStatusData(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest status_data.py
    """

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile().name
        self.status_data = opl.status_data.StatusData(self.tmpfile)

    def tierDown(self):
        del(self.status_data)
        os.remove(self.tmpfile)

    def test_filename(self):
        self.assertEqual(self.status_data._filename, self.tmpfile)

    def test_defaults(self):
        self.assertIn('name', self.status_data._data)
        self.assertIn('owner', self.status_data._data)
        self.assertIn('started', self.status_data._data)
        self.assertIn('ended', self.status_data._data)
        self.assertIn('result', self.status_data._data)

    def test_simple_set(self):
        self.status_data.set('aaa', 123)
        self.assertEqual(self.status_data._data['aaa'], 123)

    def test_nested_set(self):
        self.status_data.set('aaa.bbb', 123)
        self.assertEqual(self.status_data._data['aaa']['bbb'], 123)

    def test_simple_update(self):
        self.status_data.set('aaa', 123)
        self.status_data.set('aaa', 456)
        self.assertEqual(self.status_data._data['aaa'], 456)

    def test_nested_update(self):
        self.status_data.set('aaa.bbb', 123)
        self.status_data.set('aaa.bbb', 456)
        self.assertEqual(self.status_data._data['aaa']['bbb'], 456)

    def test_additional_set(self):
        self.status_data.set('aaa.bbb', 123)
        self.assertEqual(self.status_data._data['aaa']['bbb'], 123)
        self.status_data.set('aaa.ccc', 456)
        self.assertEqual(self.status_data._data['aaa']['bbb'], 123)
        self.assertEqual(self.status_data._data['aaa']['ccc'], 456)

    def test_simple_get(self):
        self.status_data._data['aaa'] = 123
        self.assertEqual(self.status_data.get('aaa'), 123)

    def test_nested_get(self):
        self.status_data._data['aaa'] = {}
        self.status_data._data['aaa']['bbb'] = 123
        self.assertEqual(self.status_data.get('aaa.bbb'), 123)

    def test_none_get(self):
        self.assertIsNone(self.status_data.get('aaa'))
        self.assertIsNone(self.status_data.get('aaa.bbb'))
        self.assertIsNone(self.status_data.get('aaa.bbb.ccc'))

    def test_datetime(self):
        now_plus2 = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=2)))
        now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
        self.status_data.set('aaa', now_plus2)
        self.status_data.set('bbb', now_utc)
        self.assertEqual(self.status_data.get('aaa'), now_plus2.isoformat())
        self.assertEqual(self.status_data.get('bbb'), now_utc.isoformat())
        self.assertEqual(self.status_data.get_date('aaa'), now_plus2)
        self.assertEqual(self.status_data.get_date('bbb'), now_utc)

    def test_set_now(self):
        before = datetime.datetime.now(tz=datetime.timezone.utc)
        self.status_data.set_now('aaa')
        after = datetime.datetime.now(tz=datetime.timezone.utc)
        aaa = self.status_data.get_date('aaa')
        self.assertGreaterEqual(aaa, before)
        self.assertGreaterEqual(after, aaa)

    def test_list(self):
        self.status_data._data['aaa'] = {
            'bbb': 'ccc',
            'ddd': {
                'eee': 'fff',
                'ggg': 42,
            }
        }
        exp = ['aaa.bbb', 'aaa.ddd.eee', 'aaa.ddd.ggg']
        self.assertCountEqual(self.status_data.list('aaa'), exp)

    def test_list_results(self):
        self.assertCountEqual(self.status_data.list('results'), [])

    def test_info(self):
        self.status_data.set('aaa', 123)
        self.status_data.set('bbb.ccc', 456)
        self.assertIn('Filename:', self.status_data.info())
        self.assertIn('aaa', self.status_data.info())
        self.assertIn('123', self.status_data.info())
        self.assertNotIn('bbb', self.status_data.info())
        self.assertNotIn('456', self.status_data.info())

    def test_data(self):
        f = tempfile.NamedTemporaryFile().name
        data = {
            'aaa': 123,
            'bbb': {
                'ccc': 456,
            },
            'name': '',
            'started': '',
            'ended': '',
            'result': '',
        }
        sd = opl.status_data.StatusData(f, data=data)
        self.assertEqual(sd.get('aaa'), 123)
        self.assertEqual(sd.get('bbb.ccc'), 456)
