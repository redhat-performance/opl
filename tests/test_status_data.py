#!/usr/bin/env python3

import datetime
import os
import unittest
import tempfile

import requests.exceptions

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

    def test_datetime(self):
        refference = datetime.datetime(2020, 12, 2, hour=12, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
        tests = [
            '2020-12-02T12:00:00+00:00',
            '2020-12-02T12:00:00Z',
            '2020-12-02T13:00:00+01:00',
            '2020-12-02T14:00:00+02:00',
            '2020-12-02T12:00:00.000+00:00',
            '2020-12-02T12:00:00.000Z',
            '2020-12-02T13:00:00.000+01:00',
            '2020-12-02T14:00:00.000+02:00',
            '2020-12-02T12:00:00.000000+00:00',
            '2020-12-02T12:00:00.000000Z',
            '2020-12-02T13:00:00.000000+01:00',
            '2020-12-02T14:00:00.000000+02:00',
        ]
        for t in tests:
            self.status_data.set('aaa', t)
            self.assertEqual(self.status_data.get_date('aaa'), refference)

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

    def test_long_missing_path(self):
        f = tempfile.NamedTemporaryFile().name
        data = {
            'aaa': {
                'bbb': {},
                'ccc': 123,
            },
            'name': '',
            'started': '',
            'ended': '',
            'result': '',
        }
        sd = opl.status_data.StatusData(f, data=data)
        self.assertEqual(sd.get('aaa.ccc'), 123)
        self.assertEqual(sd.get('aaa.bbb'), {})
        self.assertEqual(sd.get('aaa.bbb.ddd'), None)
        self.assertEqual(sd.get('aaa.bbb.ddd.eee'), None)

    def test_missing_path_in_none(self):
        f = tempfile.NamedTemporaryFile().name
        data = {
            'aaa': None,
            'name': '',
            'started': '',
            'ended': '',
            'result': '',
        }
        sd = opl.status_data.StatusData(f, data=data)
        self.assertEqual(sd.get('aaa'), None)
        self.assertEqual(sd.get('aaa.bbb'), None)
        self.assertEqual(sd.get('aaa.bbb.ccc'), None)

    def test_copy_original_object(self):
        something = {
            'foo': 1,
            'bar': 2,
        }
        self.status_data.set('results.something', something)
        something['baz'] = 3
        self.assertEqual(self.status_data.get('results.something.foo'), 1)
        self.assertEqual(self.status_data.get('results.something.bar'), 2)
        self.assertIn('baz', something)
        self.assertEqual(self.status_data.get('results.something.baz'), None)

    def test_set_subtree_json(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f_name = f.name
            f.write(b'{"hello":"world","foo":42,"bar":{"baz":1}}')
        self.status_data.set_subtree_json('results.xxx', f_name)
        os.unlink(f_name)
        self.assertEqual(self.status_data.get('results.xxx.hello'), 'world')
        self.assertEqual(self.status_data.get('results.xxx.foo'), 42)
        self.assertEqual(self.status_data.get('results.xxx.bar.baz'), 1)

    def test_remove_simple(self):
        self.status_data.set('results.xxx', 'should not be here')
        self.assertEqual(self.status_data.get('results.xxx'), 'should not be here')
        self.status_data.remove('results.xxx')
        self.assertIsNone(self.status_data.get('results.xxx'))

    def test_remove_missing(self):
        self.assertIsNone(self.status_data.get('results.missing'))
        self.status_data.remove('results.missing')
        self.assertIsNone(self.status_data.get('results.missing'))

    def test_file_on_http(self):
        with self.assertRaises(requests.exceptions.ConnectionError):
            status_data = opl.status_data.StatusData('http://does.not.exist/status-data-file.json')
