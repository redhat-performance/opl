#!/usr/bin/env python


import csv
import unittest.mock

HISTORY_NORMAL = """metric1,metric2
5,1000
6,995
4,1000
5,1005
"""


# https://stackoverflow.com/questions/26783678/python-mock-builtin-open-in-a-class-using-two-different-files
def get_mock_open(files: dict[str, str]):
    def my_mock_open(filename, *args, **kwargs):
        if filename in files:
            i = unittest.mock.mock_open(read_data=files[filename]).return_value
            i.name = filename
            return i
        raise FileNotFoundError(f"(mock) Unable to open {filename}")

    return unittest.mock.MagicMock(side_effect=my_mock_open)


files = {
    "/tmp/history.csv": HISTORY_NORMAL,
}

#for i in [1]:
with unittest.mock.patch("builtins.open", get_mock_open(files)) as m:
    with open("/tmp/history.csv", "r", newline="") as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            print(f"Processing {row}")
