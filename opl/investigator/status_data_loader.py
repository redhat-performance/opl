import logging

import opl.status_data


def load(fp):
    return opl.status_data.StatusData(fp.name)


def load_data(sd, paths):
    out = {}

    for path in paths:
        out[path] = sd.get(path)
        if out[path] is None:
            logging.warning(f"While loading {sd}, got None for {path}")

    logging.info(f"Loaded file {sd} and parsed {len(out.keys())} paths from it")

    return out
