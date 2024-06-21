import copy
import datetime
import json
import logging
import os
import os.path
import tempfile
import requests
import yaml
from . import date


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
        try:
            new_data = data[split_key[0]]
        except KeyError:
            if len(split_key) == 1:
                data[split_key[0]] = value
                return
            else:
                data[split_key[0]] = {}
                new_data = data[split_key[0]]

        if len(split_key) == 1:
            data[split_key[0]] = value
            return
        else:
            return self._set(new_data, split_key[1:], value)

    def set(self, multikey, value):
        """
        Recursively go through status_data data structure and set value for
        multikey. For example:

            set('a.b.c', 123)

        set:

            self._data['a']['b']['c'] = 123

        even if `self._data['a']['b']` do not exists - then it is created as
        empty dict.
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
