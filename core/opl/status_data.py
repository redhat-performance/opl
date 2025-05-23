import argparse
import copy
import datetime
import json
import logging
import os
import os.path
import pprint
import tempfile

import deepdiff

import jinja2

import requests

import tabulate

import yaml

from . import cluster_read
from . import date
from . import skelet


class StatusData:
    def __init__(self, filename, data=None):
        self.filename = filename
        if filename.startswith("http://") or filename.startswith("https://"):
            tmp = tempfile.mktemp()
            logging.info(
                f"Downloading {filename} to {tmp} and will work with that file from now on"
            )
            r = requests.get(filename, verify=False)
            with open(tmp, "wb") as fp:
                fp.write(r.content)
            filename = tmp

        self._filename = filename
        self._filename_mtime = None
        if data is None:
            self.load()
        else:
            self._data = data
            assert "name" in data
            assert "started" in data
            assert "ended" in data
            assert "result" in data

    def load(self):
        try:
            self._filename_mtime = os.path.getmtime(self._filename)
            with open(self._filename, "r") as fp:
                self._data = json.load(fp)
            logging.debug(f"Loaded status data from {self._filename}")
        except FileNotFoundError:
            self.clear()
            logging.info(f"Opening empty status data file {self._filename}")

    def __getitem__(self, key):
        logging.debug(f"Getting item {key} from {self._filename}")
        return self._data.get(key, None)

    def __setitem__(self, key, value):
        logging.debug(f"Setting item {key} from {self._filename}")
        self._data[key] = value

    def __repr__(self):
        return f"<StatusData instance version={self.get('version')} id={self.get('id')} started={self.get_date('started')}>"

    def __eq__(self, other):
        return self._data == other._data

    def __gt__(self, other):
        logging.info(f"Comparing {self} to {other}")
        return self.get_date("started") > other.get_date("started")

    def _split_mutlikey(self, multikey):
        """
        Dots delimits path in the nested dict.
        """
        if multikey == "":
            return []
        elif multikey.startswith("."):
            return multikey[1:].split(".")
        else:
            return multikey.split(".")

    def _get(self, data, split_key):
        if split_key == []:
            return data

        if not isinstance(data, dict):
            logging.warning(
                "Attempted to dive into non-dict. Falling back to return None"
            )
            return None

        try:
            new_data = data[split_key[0]]
        except KeyError:
            return None

        if len(split_key) == 1:
            return new_data
        else:
            return self._get(new_data, split_key[1:])

    def get(self, multikey):
        """
        Recursively go through status_data data structure according to
        multikey and return its value, or None. For example:

        For example:

            get(('a', 'b', 'c'))

        returns:

            self._data['a']['b']['c']

        and if say `data['a']['b']` does not exist (or any other key along
        the way), return None.
        """
        split_key = self._split_mutlikey(multikey)
        logging.debug(f"Getting {split_key} from {self._filename}")
        return self._get(self._data, split_key)

    def get_date(self, multikey):
        i = self.get(multikey)
        if i is None:
            logging.warning(f"Field {multikey} is None, so can not convert to datetime")
            return None
        return date.my_fromisoformat(i)

    def _set(self, data, split_key, value):
        current_key = split_key[0]
        last_key = len(split_key) == 1
        array_key = current_key.endswith("[]")
        if array_key:
            current_key = current_key[:-2]
        missing_key = current_key not in data

        # Check that array key is only used if this is last sub-key
        if array_key:
            assert last_key, "Arrays can only be last in the multi keys (i.e. 'aaa.bbb[]', but not 'aaa[]'.bbb)"

        # Check that we are not attempting to change type of already existing key
        if array_key and not missing_key:
            assert type(data[current_key]) == list, "You are trying to change type (e.g. 'aaa' was string and now you are trying to add to 'aaa[]')"

        if missing_key:
            if last_key:
                if array_key:
                    data[current_key] = [value]
                else:
                    data[current_key] = value
                return   # This was last key, we are done
            else:
                data[current_key] = {}   # This is not last key, so it can not be array
                return self._set(data[current_key], split_key[1:], value)
        else:
            if last_key:
                if array_key:
                    data[current_key].append(value)
                else:
                    data[current_key] = value
                return   # This was last key, we are done
            else:
                return self._set(data[current_key], split_key[1:], value)   # This is not last key, so no need to check for array

    def set(self, multikey, value):
        """
        Recursively go through status_data data structure and set value for
        multikey. For example:

            set('a.b.c', 123)

        set:

            self._data['a']['b']['c'] = 123

        even if `self._data['a']['b']` do not exists - then it is created as
        empty dict.

        It also supports adding data to lists:

            set('a.b[]', 1)
            set('a.b[]', 2)

        results in:

            self._data['a']['b'] = [1, 2]
        """
        split_key = self._split_mutlikey(multikey)
        logging.debug(f"Setting {'.'.join(split_key)} in {self._filename} to {value}")
        if isinstance(value, datetime.datetime):
            value = value.isoformat()  # make it a string with propper format
        self._set(self._data, split_key, copy.deepcopy(value))

    def set_now(self, multikey):
        """
        Set given multikey to current datetime
        """
        now = date.get_now()
        return self.set(multikey, now.isoformat())

    def set_subtree_json(self, multikey, file_path):
        """
        Set given multikey to contents of JSON formated file provided by its path
        """
        with open(file_path, "r") as fp:
            if file_path.endswith(".json"):
                data = json.load(fp)
            elif file_path.endswith(".yaml"):
                data = yaml.load(fp, Loader=yaml.SafeLoader)
            else:
                raise Exception(
                    f"Unrecognized extension of file to import: {file_path}"
                )
        return self.set(multikey, data)

    def _remove(self, data, split_key):
        try:
            new_data = data[split_key[0]]
        except KeyError:
            return

        if len(split_key) == 1:
            del data[split_key[0]]
            return
        else:
            return self._remove(new_data, split_key[1:])

    def remove(self, multikey):
        """
        Remove given multikey (and it's content) from status data file
        """
        split_key = self._split_mutlikey(multikey)
        logging.debug(f"Removing {split_key} from {self._filename}")
        self._remove(self._data, split_key)

    def list(self, multikey):
        """
        For given path, return list of all existing paths below this one
        """
        out = []
        split_key = self._split_mutlikey(multikey)
        logging.debug(f"Listing {split_key}")
        for k, v in self._get(self._data, split_key).items():
            key = ".".join(list(split_key) + [k])
            if isinstance(v, dict):
                out += self.list(key)
            else:
                out.append(key)
        return out

    def clear(self):
        """
        Default structure
        """
        self._data = {
            "name": None,
            "started": date.get_now_str(),
            "ended": None,
            "owner": None,
            "result": None,
            "results": {},
            "parameters": {},
            "measurements": {},
        }

    def info(self):
        out = ""
        out += f"Filename: {self._filename}\n"
        for k, v in self._data.items():
            if not isinstance(v, dict):
                out += f"{k}: {v}\n"
        return out

    def dump(self):
        return self._data

    def save(self, filename=None):
        """Save this status data document.

        It makes sure that on disk file was not modified since we loaded it,
        but if you provide a filename, this check is skipped.
        """
        if filename is None:
            if self._filename_mtime is not None:
                current_mtime = os.path.getmtime(self._filename)
                if self._filename_mtime != current_mtime:
                    tmp = tempfile.mktemp()
                    self._save(tmp)
                    raise Exception(
                        f"Status data file {self._filename} was modified since we loaded it so I do not want to overwrite it. Instead, saved to {tmp}"
                    )
        else:
            self._filename = filename

        self._save(self._filename)

    def _save(self, filename):
        """Just save status data document to JSON file on disk"""
        with open(filename, "w+") as fp:
            json.dump(self.dump(), fp, sort_keys=True, indent=4)
        if filename == self._filename:
            self._filename_mtime = os.path.getmtime(filename)
        logging.debug(f"Saved status data to {filename}")


def doit_set(status_data, set_this):
    for item in set_this:
        if item == "":
            logging.warning("Got empty key=value pair to set - ignoring it")
            continue

        key, value = item.split("=")

        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]

        if value == "%NOW%":
            value = date.get_now_str()
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass

        logging.debug(f"Setting {key} = {value} ({type(value)})")
        status_data.set(key, value)


def doit_remove(status_data, remove_this):
    for item in remove_this:
        status_data.remove(item)


def doit_set_subtree_json(status_data, set_this):
    for item in set_this:
        if item == "":
            logging.warning("Got empty key=value pair to set - ignoring it")
            continue

        key, value = item.split("=")

        logging.debug(f"Setting {key} = {value} (JSON file)")
        status_data.set_subtree_json(key, value)


def doit_print_oneline(status_data, get_this, get_rounding, get_delimiter):
    if not get_rounding:
        print(get_delimiter.join([str(status_data.get(i)) for i in get_this]))
    else:
        for i in get_this:
            if isinstance(status_data.get(i), float):
                print("{:.2f}".format(status_data.get(i)), end=get_delimiter)
            else:
                print("{}".format(status_data.get(i)), end=get_delimiter)
        print()


def doit_additional(status_data, additional, monitoring_start, monitoring_end, args):
    requested_info = cluster_read.RequestedInfo(
        additional,
        start=monitoring_start,
        end=monitoring_end,
        args=args,
        sd=status_data,
    )

    counter_ok = 0
    counter_bad = 0
    for k, v in requested_info:
        if k is None:
            counter_bad += 1
        else:
            status_data.set(k, v)
            counter_ok += 1

    print(
        f"Gathered {counter_ok} `ok` data points. Not gathered {counter_bad} `bad` data points"
    )


def doit_info(status_data):
    print(status_data.info())


def main():
    parser = argparse.ArgumentParser(
        description="Work with status data file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--set",
        nargs="*",
        default=[],
        help='Set key=value data. If value is "%%NOW%%", current date&time is added',
    )
    parser.add_argument(
        "--set-now", nargs="*", default=[], help="Set key to current date&time"
    )
    parser.add_argument(
        "--set-subtree-json",
        nargs="*",
        default=[],
        help="Set key to structure from json or yaml formated file (detected by *.json or *.yaml file extension)",
    )
    parser.add_argument(
        "--get", nargs="*", default=[], help="Print value for given key(s)"
    )
    parser.add_argument("--remove", nargs="*", default=[], help="Remove given key(s)")
    parser.add_argument(
        "--additional",
        type=argparse.FileType("r"),
        help="Gather more info as specified by the cluster_read.py compatible yaml file",
    )
    parser.add_argument(
        "--monitoring-start",
        type=date.my_fromisoformat,
        help="Start of monitoring interval in ISO 8601 format in UTC with seconds precision",
    )
    parser.add_argument(
        "--monitoring-end",
        type=date.my_fromisoformat,
        help="End of monitoring interval in ISO 8601 format in UTC with seconds precision",
    )
    parser.add_argument(
        "--monitoring-raw-data-dir",
        type=cluster_read.dir_path,
        help="Provide a direcotory if you want raw monitoring data to be dumped in CSV files form",
    )
    parser.add_argument(
        "--end",
        action="store_true",
        help='"started" is set when the status data file is created, "ended" is set when this is used',
    )
    parser.add_argument(
        "--info", action="store_true", help="Show basic info from status data file"
    )
    parser.add_argument(
        "--decimal-rounding",
        action="store_true",
        help="Rounding a number to its hundredths, leaving 2 numbers after decimal point",
    )
    parser.add_argument(
        "--delimiter",
        default="\t",
        help='When returning more "--get" fields, delimit them with this (default is tab)',
    )
    for name, plugin in cluster_read.PLUGINS.items():
        plugin.add_args(parser)

    with skelet.test_setup(parser) as (args, status_data):
        if len(args.set) > 0:
            doit_set(status_data, args.set)
        if len(args.set_now) > 0:
            doit_set(status_data, [k + "=%NOW%" for k in args.set_now])
        if len(args.set_subtree_json) > 0:
            doit_set_subtree_json(status_data, args.set_subtree_json)
        if len(args.get) > 0:
            doit_print_oneline(
                status_data, args.get, args.decimal_rounding, args.delimiter
            )
        if len(args.remove) > 0:
            doit_remove(status_data, args.remove)
        if args.additional:
            doit_additional(
                status_data,
                args.additional,
                args.monitoring_start,
                args.monitoring_end,
                args,
            )
        if args.end:
            doit_set(status_data, ["ended=%NOW%"])
        if args.info:
            doit_info(status_data)


def main_diff():
    parser = argparse.ArgumentParser(
        description="Compare two status data files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("first", nargs=1, help="First file to compare")
    parser.add_argument("second", nargs=1, help="Second file to compare")
    parser.add_argument("--report", action="store_true", help="Show formated report")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    first = StatusData(args.first[0])
    second = StatusData(args.second[0])

    diff = deepdiff.DeepDiff(first._data, second._data, view="tree")
    if args.report:
        print(f"Keys: {', '.join(diff.keys())}")
        if "dictionary_item_added" in diff:
            print("\nDictionary items added:\n")
            table = []
            for i in diff["dictionary_item_added"]:
                table.append([i.path(), i.t2])
            print(tabulate.tabulate(table, headers=["path", "added value"]))
        if "dictionary_item_removed" in diff:
            print("\nDictionary items removed:\n")
            table = []
            for i in diff["dictionary_item_removed"]:
                table.append([i.path(), i.t1])
            print(tabulate.tabulate(table, headers=["path", "removed value"]))
        if "values_changed" in diff:
            print("\nValues changed:\n")
            table = []
            for i in diff["values_changed"]:
                d = None
                try:
                    first = float(i.t1)
                    second = float(i.t2)
                    d_raw = (second - first) / first * 100
                    if abs(d_raw) < 1:
                        d = f"{d_raw:.3f}"
                    else:
                        d = f"{d_raw:.0f}"
                except (ValueError, ZeroDivisionError):
                    pass
                table.append([i.path(), i.t1, i.t2, d])
            print(
                tabulate.tabulate(
                    table, headers=["path", "first", "second", "change [%]"]
                )
            )
        if "type_changes" in diff:
            print("\nTypes changed:\n")
            table = []
            for i in diff["type_changes"]:
                table.append([i.path(), type(i.t1), type(i.t2)])
            print(tabulate.tabulate(table, headers=["path", "first", "second"]))
    else:
        pprint.pprint(diff)


def main_report():
    parser = argparse.ArgumentParser(
        description="Create a report using provided template from status" " data file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("template", help="Report template file to use")
    parser.add_argument("status_data", help="Status data file to format")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    # Load Jinja2 template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(args.template))
    )
    template = env.get_template(os.path.basename(args.template))

    # Load status data document
    data = StatusData(args.status_data)

    print(template.render({"data": data}))
