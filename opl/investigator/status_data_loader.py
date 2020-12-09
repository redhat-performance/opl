import logging

import opl.status_data


def load(fp, paths):
    out = {}

    sd = opl.status_data.StatusData(fp.name)

    for path in paths:
        out[path] = sd.get(path)
        if out[path] is None:
            logging.warning(f"While loading {fp.name}, got None for {path}")

    logging.info(f"Loaded file {fp.name} and parsed {len(out.keys())} paths from it")

    return out, sd
