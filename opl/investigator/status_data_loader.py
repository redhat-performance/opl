import logging

import opl.status_data


def load(fp, paths):
    out = {}

    sd = opl.status_data.StatusData(fp.name)

    for path in paths:
        out[path] = sd.get(path)
        assert out[path] is not None, f"Check if {out[path]} is None"

    logging.info(f"Loaded file {fp.name} and parsed {len(out.keys())} paths from it")

    return out
