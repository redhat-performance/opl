import csv
import datetime
import os


def store(filename, decisions):
    # This is our workaround on how to add additional metadata about the decision
    job_name = os.environ.get("JOB_NAME", "")
    build_url = os.environ.get("BUILD_URL", "")

    for decision in decisions:
        decision["job_name"] = job_name
        decision["build_url"] = build_url
        decision["uploaded"] = datetime.datetime.utcnow().isoformat()

    fieldnames = []
    for d in decisions:
        for k in d.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with open(filename, "w") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)

        writer.writeheader()

        for decision in decisions:
            writer.writerow(decision)
