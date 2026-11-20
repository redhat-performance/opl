#!/usr/bin/env python3
"""Tests for the opl.status_data module."""

# pylint: disable=protected-access  # tests verify internal data structures directly

import datetime
import json
import os
import tempfile
import time
import unittest

import requests.exceptions

from .context import opl


class TestStatusData(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest status_data.py
    """

    def setUp(self):
        """Prepare StatusData object backed by a temp file."""
        self.tmpfile = tempfile.NamedTemporaryFile().name  # pylint: disable=consider-using-with  # only the unique name is needed
        self.status_data = opl.status_data.StatusData(self.tmpfile)

    def tierDown(self):  # pylint: disable=invalid-name  # intentionally not unittest's tearDown: cleanup runs via del below
        """Drop the StatusData object and remove the temp file."""
        del self.status_data
        os.remove(self.tmpfile)

    def test_filename(self):
        """StatusData must remember the file it was created with."""
        self.assertEqual(self.status_data._filename, self.tmpfile)

    def test_defaults(self):
        """New StatusData must contain default metadata keys."""
        self.assertIn("name", self.status_data._data)
        self.assertIn("owner", self.status_data._data)
        self.assertIn("started", self.status_data._data)
        self.assertIn("ended", self.status_data._data)
        self.assertIn("result", self.status_data._data)

    def test_simple_set(self):
        """set() must store a top-level value."""
        self.status_data.set("aaa", 123)
        self.assertEqual(self.status_data._data["aaa"], 123)

    def test_nested_set(self):
        """set() must create nested dicts for dotted paths."""
        self.status_data.set("aaa.bbb", 123)
        self.assertEqual(self.status_data._data["aaa"]["bbb"], 123)

    def test_simple_update(self):
        """set() must overwrite an existing top-level value."""
        self.status_data.set("aaa", 123)
        self.status_data.set("aaa", 456)
        self.assertEqual(self.status_data._data["aaa"], 456)

    def test_nested_update(self):
        """set() must overwrite an existing nested value."""
        self.status_data.set("aaa.bbb", 123)
        self.status_data.set("aaa.bbb", 456)
        self.assertEqual(self.status_data._data["aaa"]["bbb"], 456)

    def test_additional_set(self):
        """set() must add to existing data without touching it."""
        self.status_data.set("aaa.bbb", 123)
        self.assertEqual(self.status_data._data["aaa"]["bbb"], 123)
        self.status_data.set("aaa.ccc", 456)
        self.assertEqual(self.status_data._data["aaa"]["bbb"], 123)
        self.assertEqual(self.status_data._data["aaa"]["ccc"], 456)

    def test_set_with_leading_dot(self):
        """set() must ignore a leading dot in the path."""
        self.status_data.set(".aaa", 123)
        self.assertEqual(self.status_data._data["aaa"], 123)
        self.status_data.set(".bbb.ccc", 456)
        self.assertEqual(self.status_data._data["bbb"]["ccc"], 456)
        self.status_data.set("..zzz", 789)
        self.assertEqual(self.status_data._data[""]["zzz"], 789)

    def test_simple_get(self):
        """get() must return a top-level value."""
        self.status_data._data["aaa"] = 123
        self.assertEqual(self.status_data.get("aaa"), 123)

    def test_nested_get(self):
        """get() must return a nested value via dotted path."""
        self.status_data._data["aaa"] = {}
        self.status_data._data["aaa"]["bbb"] = 123
        self.assertEqual(self.status_data.get("aaa.bbb"), 123)

    def test_get_with_leading_dot(self):
        """get() must ignore a leading dot in the path."""
        self.status_data._data["aaa"] = 123
        self.status_data._data["bbb"] = {}
        self.status_data._data["bbb"]["ccc"] = 456
        self.assertEqual(self.status_data.get("aaa"), 123)
        self.assertEqual(self.status_data.get("bbb.ccc"), 456)
        self.assertEqual(self.status_data.get(".aaa"), 123)
        self.assertEqual(self.status_data.get(".bbb.ccc"), 456)
        self.assertEqual(self.status_data.get("..aaa"), None)
        self.assertEqual(self.status_data.get(".zzz"), None)

    def test_none_get(self):
        """get() must return None for a path inside a None value."""
        self.assertIsNone(self.status_data.get("aaa"))
        self.assertIsNone(self.status_data.get("aaa.bbb"))
        self.assertIsNone(self.status_data.get("aaa.bbb.ccc"))

    def test_datetime(self):
        """Datetime values must survive a save/load round-trip."""
        now_plus2 = datetime.datetime.now(
            tz=datetime.timezone(datetime.timedelta(hours=2))
        )
        now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
        self.status_data.set("aaa", now_plus2)
        self.status_data.set("bbb", now_utc)
        self.assertEqual(self.status_data.get("aaa"), now_plus2.isoformat())
        self.assertEqual(self.status_data.get("bbb"), now_utc.isoformat())
        self.assertEqual(self.status_data.get_date("aaa"), now_plus2)
        self.assertEqual(self.status_data.get_date("bbb"), now_utc)

    def test_datetime_format(self):
        """Saved datetime values must use a parseable format."""
        refference = datetime.datetime(
            2020,
            12,
            2,
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=datetime.timezone.utc,
        )
        tests = [
            "2020-12-02T12:00:00+00:00",
            "2020-12-02T12:00:00Z",
            "2020-12-02T13:00:00+01:00",
            "2020-12-02T14:00:00+02:00",
            "2020-12-02T12:00:00.000+00:00",
            "2020-12-02T12:00:00.000Z",
            "2020-12-02T13:00:00.000+01:00",
            "2020-12-02T14:00:00.000+02:00",
            "2020-12-02T12:00:00.000000+00:00",
            "2020-12-02T12:00:00.000000Z",
            "2020-12-02T13:00:00.000000+01:00",
            "2020-12-02T14:00:00.000000+02:00",
        ]
        for t in tests:
            self.status_data.set("aaa", t)
            self.assertEqual(self.status_data.get_date("aaa"), refference)

    def test_set_now(self):
        """set_now() must store the current timestamp."""
        before = datetime.datetime.now(tz=datetime.timezone.utc)
        self.status_data.set_now("aaa")
        after = datetime.datetime.now(tz=datetime.timezone.utc)
        aaa = self.status_data.get_date("aaa")
        self.assertGreaterEqual(aaa, before)
        self.assertGreaterEqual(after, aaa)

    def test_list(self):
        """get() must return a list value stored under a key."""
        self.status_data._data["aaa"] = {
            "bbb": "ccc",
            "ddd": {
                "eee": "fff",
                "ggg": 42,
            },
        }
        exp = ["aaa.bbb", "aaa.ddd.eee", "aaa.ddd.ggg"]
        self.assertCountEqual(self.status_data.list("aaa"), exp)

    def test_list_results(self):
        """Data with a 'results' list must be handled."""
        self.assertCountEqual(self.status_data.list("results"), [])

    def test_info(self):
        """info() must render data without excluded keys."""
        self.status_data.set("aaa", 123)
        self.status_data.set("bbb.ccc", 456)
        self.assertIn("Filename:", self.status_data.info())
        self.assertIn("aaa", self.status_data.info())
        self.assertIn("123", self.status_data.info())
        self.assertNotIn("bbb", self.status_data.info())
        self.assertNotIn("456", self.status_data.info())

    def test_data(self):
        """StatusData must accept initial data and serve it via get()."""
        f = tempfile.NamedTemporaryFile().name  # pylint: disable=consider-using-with  # only the unique name is needed
        data = {
            "aaa": 123,
            "bbb": {
                "ccc": 456,
            },
            "name": "",
            "started": "",
            "ended": "",
            "result": "",
        }
        sd = opl.status_data.StatusData(f, data=data)
        self.assertEqual(sd.get("aaa"), 123)
        self.assertEqual(sd.get("bbb.ccc"), 456)

    def test_long_missing_path(self):
        """get() must return None for missing nested paths."""
        f = tempfile.NamedTemporaryFile().name  # pylint: disable=consider-using-with  # only the unique name is needed
        data = {
            "aaa": {
                "bbb": {},
                "ccc": 123,
            },
            "name": "",
            "started": "",
            "ended": "",
            "result": "",
        }
        sd = opl.status_data.StatusData(f, data=data)
        self.assertEqual(sd.get("aaa.ccc"), 123)
        self.assertEqual(sd.get("aaa.bbb"), {})
        self.assertEqual(sd.get("aaa.bbb.ddd"), None)
        self.assertEqual(sd.get("aaa.bbb.ddd.eee"), None)

    def test_missing_path_in_none(self):
        """get() must return None when a parent value is None."""
        f = tempfile.NamedTemporaryFile().name  # pylint: disable=consider-using-with  # only the unique name is needed
        data = {
            "aaa": None,
            "name": "",
            "started": "",
            "ended": "",
            "result": "",
        }
        sd = opl.status_data.StatusData(f, data=data)
        self.assertEqual(sd.get("aaa"), None)
        self.assertEqual(sd.get("aaa.bbb"), None)
        self.assertEqual(sd.get("aaa.bbb.ccc"), None)

    def test_copy_original_object(self):
        """Constructor must not share data with the passed object."""
        something = {
            "foo": 1,
            "bar": 2,
        }
        self.status_data.set("results.something", something)
        something["baz"] = 3
        self.assertEqual(self.status_data.get("results.something.foo"), 1)
        self.assertEqual(self.status_data.get("results.something.bar"), 2)
        self.assertIn("baz", something)
        self.assertEqual(self.status_data.get("results.something.baz"), None)

    def test_set_subtree_json(self):
        """doit_set_subtree_json() must merge a JSON subtree."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            f_name = f.name
            f.write(b'{"hello":"world","foo":42,"bar":{"baz":1}}')
        self.status_data.set_subtree_json("results.xxx_json", f_name)
        os.unlink(f_name)
        self.assertEqual(self.status_data.get("results.xxx_json.hello"), "world")
        self.assertEqual(self.status_data.get("results.xxx_json.foo"), 42)
        self.assertEqual(self.status_data.get("results.xxx_json.bar.baz"), 1)

    def test_set_subtree_yaml(self):
        """doit_set_subtree_yaml() must merge a YAML subtree."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as f:
            f_name = f.name
            f.write(b"hello: world\nfoo: 42\nbar:\n  baz: 1")
        self.status_data.set_subtree_json("results.xxx_yaml", f_name)
        os.unlink(f_name)
        self.assertEqual(self.status_data.get("results.xxx_yaml.hello"), "world")
        self.assertEqual(self.status_data.get("results.xxx_yaml.foo"), 42)
        self.assertEqual(self.status_data.get("results.xxx_yaml.bar.baz"), 1)

    def test_remove_simple(self):
        """remove() must delete an existing key."""
        self.status_data.set("results.xxx", "should not be here")
        self.assertEqual(self.status_data.get("results.xxx"), "should not be here")
        self.status_data.remove("results.xxx")
        self.assertIsNone(self.status_data.get("results.xxx"))

    def test_remove_missing(self):
        """remove() must pass on a missing key."""
        self.assertIsNone(self.status_data.get("results.missing"))
        self.status_data.remove("results.missing")
        self.assertIsNone(self.status_data.get("results.missing"))

    def test_file_on_http(self):
        """StatusData must support loading data from an URL."""
        with self.assertRaises(requests.exceptions.ConnectionError):
            _ = opl.status_data.StatusData(
                "http://does.not.exist/status-data-file.json"
            )

    def test_comment(self):
        """add_comment() must append and persist a comment."""
        comment = {
            "author": "Foo Bar",
            "date": opl.date.get_now_str(),
            "text": "Some comment",
        }
        self.status_data.set("comments", [])
        comments = self.status_data.get("comments")
        comments.append(comment)
        self.assertEqual(self.status_data.get("comments")[0], comment)
        data = self.status_data.dump()
        sd_new = opl.status_data.StatusData("/tmp/aaa.json", data=data)
        self.assertEqual(sd_new.get("comments")[0], comment)

    def test_save(self):
        """save() must persist changes to the file."""
        tmp = tempfile.mktemp()
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write(
                '{"name":"test","started":"2024-01-31T12:19:42,794470088+00:00","results":{"number":42}}'
            )
        sd = opl.status_data.StatusData(tmp)
        self.assertEqual(sd.get("name"), "test")
        self.assertEqual(sd.get("started"), "2024-01-31T12:19:42,794470088+00:00")
        self.assertEqual(sd.get("results.number"), 42)
        self.assertEqual(sd.get("results.number_new"), None)
        sd.set("results.number_new", -3.14)
        sd.save()
        sd_new = opl.status_data.StatusData(tmp)
        self.assertEqual(sd_new.get("name"), "test")
        self.assertEqual(sd_new.get("started"), "2024-01-31T12:19:42,794470088+00:00")
        self.assertEqual(sd_new.get("results.number"), 42)
        self.assertEqual(sd_new.get("results.number_new"), -3.14)

    def test_load(self):
        """load() must re-read changed data from the file."""
        tmp = tempfile.mktemp()
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write('{"name":"test","results":{"number":42}}')
        sd = opl.status_data.StatusData(tmp)
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write('{"name":"test","results":{"number":42,"number_new":-3.14}}')
        self.assertEqual(sd.get("name"), "test")
        self.assertEqual(sd.get("results.number"), 42)
        self.assertEqual(sd.get("results.number_new"), None)
        sd.load()
        self.assertEqual(sd.get("name"), "test")
        self.assertEqual(sd.get("results.number"), 42)
        self.assertEqual(sd.get("results.number_new"), -3.14)

    def test_override(self):
        """save() must refuse to overwrite a file changed on disk."""
        tmp = tempfile.mktemp()
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write('{"name":"test","results":{"number":42}}')
        sd = opl.status_data.StatusData(tmp)
        sd.set("results.number_new", -3.14)

        time.sleep(
            0.001
        )  # workaround, see https://stackoverflow.com/a/77913929/2229885
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write(
                '{"name":"test","results":{"number":42,"foo":"bar"}}'
            )  # file on the disk changed

        with self.assertRaises(Exception) as context:
            sd.save()  # file changed since last load so this will raise exception

        tmp_new = str(context.exception).rsplit(" ", maxsplit=1)[
            -1
        ]  # exception message contains emergency file with current object data
        with open(tmp_new, "r", encoding="utf-8") as fd:
            tmp_new_data = json.load(fd)
            self.assertEqual(
                tmp_new_data["results"]["number_new"], -3.14
            )  # changes made before emergency save are there
        self.assertEqual(sd.get("results.number_new"), -3.14)

        sd.load()  # load changed file, drop changes in the object

        self.assertEqual(
            sd.get("results.number_new"), None
        )  # changes made to old object are lost
        self.assertEqual(
            sd.get("results.foo"), "bar"
        )  # this was loaded from modified file

        sd.save()  # save should work now as file did not changed since last load

    def test_force_save(self):
        """save(path) must force saving to a changed file."""
        tmp = tempfile.mktemp()
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write('{"name":"test","results":{"number":42}}')
        sd = opl.status_data.StatusData(tmp)
        sd.set("results.number_new", -3.14)

        time.sleep(
            0.001
        )  # workaround, see https://stackoverflow.com/a/77913929/2229885
        with open(tmp, "w", encoding="utf-8") as fp:
            fp.write(
                '{"name":"test","results":{"number":42,"foo":"bar"}}'
            )  # file on the disk changed

        with self.assertRaises(Exception) as _:
            sd.save()  # file changed since last load so this will raise exception
        sd.save(tmp)  # providing a path means forcing save

        # sd_new = opl.status_data.StatusData(tmp)
        opl.status_data.StatusData(tmp)
        self.assertEqual(sd.get("results.number_new"), -3.14)
        self.assertEqual(sd.get("results.foo"), None)

    def test_simple_set_to_list(self):
        """set() with '[]' must append to a top-level list."""
        self.status_data.set("aaa[]", 123)
        self.assertEqual(self.status_data._data["aaa"], [123])
        self.status_data.set("aaa[]", 456)
        self.assertEqual(self.status_data._data["aaa"], [123, 456])
        self.status_data.set("aaa[]", "Hello")
        self.assertEqual(self.status_data._data["aaa"], [123, 456, "Hello"])

    def test_nested_set_to_list(self):
        """set() with '[]' must append to a nested list."""
        self.status_data.set("aaa.bbb.ccc[]", 123)
        self.assertEqual(self.status_data._data["aaa"]["bbb"]["ccc"], [123])
        self.status_data.set("aaa.bbb.ccc[]", 456)
        self.assertEqual(self.status_data._data["aaa"]["bbb"]["ccc"], [123, 456])

    def test_dicts_set_to_list(self):
        """set() with '[]' must append dicts to a list."""
        d1 = {"id": 42, "name": "Universe"}
        d2 = {"id": 0, "name": "Sun"}
        self.status_data.set("aaa[]", d1)
        self.status_data.set("aaa[]", d2)
        self.assertEqual(self.status_data._data["aaa"], [d1, d2])

    def test_not_last_set_to_list(self):
        """set() with '[]' not at path end must raise."""
        with self.assertRaises(AssertionError):
            self.status_data.set("aaa[].bbb", 123)

    def test_type_missmatch_set_to_list(self):
        """set() with '[]' on a non-list must raise."""
        self.status_data.set("aaa", 123)
        with self.assertRaises(AssertionError):
            self.status_data.set("aaa[]", 123)

    def test_invalid_set_argument(self):
        """doit_set*() must raise on malformed arguments."""
        with self.assertRaises(ValueError):
            opl.status_data.doit_set(self.status_data, ["=somevalue"])
        with self.assertRaises(ValueError):
            opl.status_data.doit_set(self.status_data, ["no_equals_sign"])
        with self.assertRaises(ValueError):
            opl.status_data.doit_set_subtree_json(self.status_data, ["=somevalue"])
        with self.assertRaises(ValueError):
            opl.status_data.doit_set_subtree_json(self.status_data, ["no_equals_sign"])

    def test_valid_empty_value_set_argument(self):
        """doit_set() must accept an empty value."""
        opl.status_data.doit_set(self.status_data, ["mykey="])
        self.assertEqual(self.status_data.get("mykey"), "")
