"""Load tabular data from CSV files."""

import csv
import logging


def load(fp, columns):
    """Load given columns from CSV file into dict of lists."""
    out = {}

    for col in columns:
        out[col] = []

    reader = csv.DictReader(fp)

    for row in reader:
        for col, values in out.items():
            values.append(float(row[col]))

    logging.info(
        "Loaded file %s and parsed %s columns with %s rows", fp.name, len(out.keys()), len(next(iter(out.values())))
    )

    return out
