#!/usr/bin/env python3

import junitparser
import tempfile
import unittest

from .context import opl


class TestJUnitXmlPlus(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest junit_cli.py
    """

    def setUp(self):
        tmpfile = tempfile.NamedTemporaryFile(delete=True).name
        self.junit = opl.junit_cli.JUnitXmlPlus()
        self.junit.filepath = tmpfile

    def tierDown(self):
        self.junit.delete()

    def test_fromfile_or_new(self):
        tmpfile = tempfile.NamedTemporaryFile(delete=True).name
        self.junit.write(tmpfile)
        junit = opl.junit_cli.JUnitXmlPlus.fromfile_or_new(tmpfile)
        self.assertEqual(junit.filepath, tmpfile)

        tmpfile = tempfile.NamedTemporaryFile(delete=True).name
        junit = opl.junit_cli.JUnitXmlPlus.fromfile_or_new(tmpfile)
        self.assertEqual(junit.filepath, tmpfile)

    def test_add_to_suite(self):
        tc1 = {
            'name': 'bbb',
            'result': 'PASS',
            'message': None,
            'system-out': None,
            'system-err': None,
            'start': opl.date.my_fromisoformat('2019-12-18T14:05:33+01:00'),
            'end': opl.date.my_fromisoformat('2019-12-18T14:10:56+01:00'),
        }
        tc2 = tc1.copy()
        tc2['name'] = 'ccc'
        tc2['result'] = 'FAIL'

        self.junit.add_to_suite('aaa', tc1)
        self.junit.add_to_suite('aaa', tc2)

        suite = next(iter(self.junit))
        self.assertEqual(suite.name, 'aaa')
        suite_iter = iter(suite)
        case1 = next(suite_iter)
        case2 = next(suite_iter)

        self.assertEqual(case1.name, 'bbb')
        self.assertEqual(case1.result, [])
        self.assertEqual(case2.name, 'ccc')
        self.assertEqual(len(case2.result), 1)
        self.assertEqual(type(case2.result[0]), junitparser.junitparser.Failure)
