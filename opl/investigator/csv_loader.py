import csv
import logging


def load(fp, columns):
    out = {}

    for col in columns:
        out[col] = []

    reader = csv.DictReader(fp)

    for row in reader:
        for col in out.keys():
            out[col].append(float(row[col]))

    logging.info(f"Loaded file {fp.name} and parsed {len(out.keys())} columns with {len(next(iter(out.values())))} rows")

    return out
