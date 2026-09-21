"""Load data from a status data file."""

import logging

import opl.status_data


def load(fp):
    """Load a status data file."""
    return opl.status_data.StatusData(fp.name)


def load_data(sd, paths):
    """Extract given paths from the status data."""
    out = {}

    for path in paths:
        out[path] = sd.get(path)
        if out[path] is None:
            logging.warning("While loading %s, got None for %s", sd, path)

    logging.info("Loaded file %s and parsed %s paths from it", sd, len(out.keys()))

    return out
