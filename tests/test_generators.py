#!/usr/bin/env python3
"""Tests for the opl.generators.generic module."""

import os
import tempfile
import unittest

from .context import opl


class TestGenericGenerator(unittest.TestCase):
    """Tests for GenericGenerator."""

    def test_count(self):
        """Generator must produce the requested number of messages."""
        _, template = tempfile.mkstemp(
            dir=os.path.dirname(opl.generators.generic.__file__), text=True
        )

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
        """Generator must support the opl_gen.gen_uuid() template helper."""
        _, template = tempfile.mkstemp(
            dir=os.path.dirname(opl.generators.generic.__file__), text=True
        )

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
