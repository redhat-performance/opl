"""Load data from a directory of status data files."""

import logging
import os

import opl.status_data


def _matches(sd, matchers):
    for key, val in matchers.items():
        if sd.get(key) != val:
            logging.debug('File %s key %s does not match %s != %s', sd, key, val, sd.get(key))
            return False

    logging.debug('File %s matches with matchers %s', sd, matchers)
    return True


def load(data_dir, data_matchers, paths):
    """Load given paths from status data files matching the matchers."""
    out = {}

    for path in paths:
        out[path] = []

    for dirpath, _dirnames, filenames in os.walk(data_dir):
        for f in filenames:
            if not f.endswith(".json") or not os.path.isfile(os.path.join(dirpath, f)):
                continue

            sd = opl.status_data.StatusData(os.path.join(dirpath, f))

            if _matches(sd, data_matchers):
                for path in paths:
                    tmp = sd.get(path)
                    if tmp is not None:
                        out[path].append(tmp)

    logging.debug('Loaded %s', out)
    return out
