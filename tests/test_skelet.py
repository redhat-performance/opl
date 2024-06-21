#!/usr/bin/env python3

import unittest
import argparse
import datetime

from .context import opl


class TestSkelet(unittest.TestCase):
    def test_test_setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--fake_arg", help="Just to catch test file name when calling tests"
        )
        with opl.skelet.test_setup(parser) as (args, status_data):
            self.assertIn("debug", args)

    def test_retry_on_traceback(self):
        wait_seconds = 0.1

        @opl.retry.retry_on_traceback(max_attempts=0, wait_seconds=wait_seconds)
        def failing1():
            return 1 / 0

        before = datetime.datetime.now()
        with self.assertRaises(ZeroDivisionError) as _:
            failing1()
        after = datetime.datetime.now()

        self.assertGreaterEqual(wait_seconds, (after - before).total_seconds())

        @opl.retry.retry_on_traceback(max_attempts=1, wait_seconds=wait_seconds)
        def failing2():
            return 1 / 0

        before = datetime.datetime.now()
        with self.assertRaises(ZeroDivisionError) as _:
            failing2()
        after = datetime.datetime.now()

        self.assertGreaterEqual((after - before).total_seconds(), wait_seconds)

        wait_seconds = 10

        before = datetime.datetime.now()
        with self.assertRaises(AssertionError) as _:

            @opl.retry.retry_on_traceback(max_attempts=-1, wait_seconds=wait_seconds)
            def failing():
                return 1 / 0

        after = datetime.datetime.now()

        self.assertLess((after - before).total_seconds(), wait_seconds)
