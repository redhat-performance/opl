#!/usr/bin/env python3
"""Tests for opl.generators."""

import os
import tempfile
import unittest

from .context import opl

# Test methods and classes are self-documenting via descriptive names.
# pylint: disable=missing-function-docstring, missing-class-docstring


class TestGenericGenerator(unittest.TestCase):

    def test_count(self):
        _, template = tempfile.mkstemp(dir=os.path.dirname(opl.generators.generic.__file__), text=True)

        try:
            with open(template, "w", encoding="utf-8") as fd:
                fd.write('{"foo": "bar"}')

            gg = opl.generators.generic.GenericGenerator(3, os.path.basename(template))

            counter = 0
            for message in gg:
                self.assertIsInstance(message, tuple)
                counter += 1

            self.assertEqual(counter, 3)
        finally:
            os.remove(template)

    def test_uuids(self):
        _, template = tempfile.mkstemp(dir=os.path.dirname(opl.generators.generic.__file__), text=True)

        try:
            with open(template, "w", encoding="utf-8") as fd:
                fd.write('{"x": "{{ opl_gen.gen_uuid() }}"}')

            gg = opl.generators.generic.GenericGenerator(3, os.path.basename(template))

            uuids = []
            for message in gg:
                self.assertEqual(len(message[1]["x"]), 36)
                uuids.append(message[1]["x"])

            self.assertEqual(len(uuids), 3)
        finally:
            os.remove(template)
