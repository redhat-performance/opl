"""Store investigation decisions to CSV file."""

import csv
import datetime
import os


def store(filename, decisions):
    """Write decisions to CSV file."""
    # This is our workaround on how to add additional metadata about the decision
    job_name = os.environ.get("JOB_NAME", "")
    build_url = os.environ.get("BUILD_URL", "")

    for decision in decisions:
        decision["job_name"] = job_name
        decision["build_url"] = build_url
        decision["uploaded"] = datetime.datetime.now(
            tz=datetime.timezone.utc
        ).isoformat()

    fieldnames = []
    for d in decisions:
        for k in d.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with open(filename, "w", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)

        writer.writeheader()

        for decision in decisions:
            writer.writerow(decision)
