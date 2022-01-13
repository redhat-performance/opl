import logging
import os

import opl.status_data


def _matches(sd, matchers):
    for key, val in matchers.items():
        if sd.get(key) != val:
            logging.debug(f"File {sd} key {key} does not match {val} != {sd.get(key)}")
            return False

    logging.debug(f"File {sd} matches with matchers {matchers}")
    return True


def load(data_dir, data_matchers, paths):
    out = {}

    for path in paths:
        out[path] = []

    for (dirpath, dirnames, filenames) in os.walk(data_dir):
        for f in filenames:
            if not f.endswith('.json') or not os.path.isfile(os.path.join(dirpath, f)):
                continue

            sd = opl.status_data.StatusData(os.path.join(dirpath, f))

            if _matches(sd, data_matchers):
                for path in paths:
                    tmp = sd.get(path)
                    if tmp is not None:
                        out[path].append(tmp)

    logging.debug(f"Loaded {out}")
    return out
