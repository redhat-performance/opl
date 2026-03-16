MBU products perf&scale library
======================

OPL library
-----------

Contains various helpers for not only RHCloud performance testing.

Repository Structure
--------------------

This repository uses a split-directory workspace layout to cleanly separate lightweight core tools from those requiring heavy dependencies (like `kafka-python`, `psycopg2-binary`, `locust`). Python's implicit namespace packages (PEP 420) are used so that imports like `import opl.some_module` work seamlessly across both directories.

* `core/opl/` - Contains the lightweight, minimal-dependency core tools.
* `extras/opl/` - Contains tools and generators that require heavier dependencies.

Generic command-line tools
--------------------------

There is couple of tools used mostly to integrate with CPT and comp.:

* `cluster_read.py` - Library (and command-line tool) to get data in a ways
  defined in a config file. It can execute command, read from Prometheus or
  Grafana. It is used by `status_data.py` to enritch status data files with
  facts (as defined in per-test config file). Usually it is info about
  the cluster (using `oc ... | jq ...` commands) or monitoring data from
  Prometheus. E.g. see `core/opl/cluster_read_example.yaml`.
* `pass_or_fail.py` - Tool which uses simple statistic in an attempt to
  decide if latest test result is PASS or FAIL when compared to historical
  results. Example of the config file is in
  `core/opl/investigator/sample_config.yaml`.
* `junit_cli.py` - Script to manipulate JUnit XML file from CLI. It is
  used by Satellite CPT.
* `status_data.py` - Library (and command-line tool) to manipulate status
  data files.
* `status_data_report.py` - Tool to render Jinja2 template with data from
  status data file. It is used by tests to provide final summary without need
  to write per-test tool which would do it - Jinja2 template seems to provide
  enough logick for what is needed in the output. Each test have its own
  template - e.g. see `core/opl/status_data_report.txt`.
* `status_data_diff.py` - Convenience tool to show differences in two status
  data files.

These tools are only used by tests:

* `script-skip-to-end.py` - Script to skip to the end of Kafka queues for
  given consumer group (it should be trivial given python-kafka docs, but
  simplest way did not worked for me)
* `script-manage-db.py` - Helper script to manipulate with utility DB.
  Consumes config with list of tables relevant for given test and SQL needed
  to create them. E.g. see `extras/opl/sample-tables.yaml`

Installation
------------

You can install the full library or just the lightweight core tools.

**Full Installation:**

Installs all tools, including those with heavy dependencies.

    python -m venv venv
    source venv/bin/activate
    python -m pip install git+https://github.com/redhat-performance/opl.git

**Core Installation:**

Installs only the lightweight core tools from `core/opl/` to minimize dependency footprint.

    python -m venv venv
    source venv/bin/activate
    python3 -m pip install --no-cache-dir -e "git+https://github.com/redhat-performance/opl.git#egg=opl-rhcloud-perf-team-core&subdirectory=core"

**Extras Installation:**

If you choose to install only the extras package, it is your responsibility to also install the core package, as extras modules depend on core functionality:

    python3 -m pip install "git+https://github.com/redhat-performance/opl.git#egg=opl-rhcloud-perf-team-core&subdirectory=core"
    python3 -m pip install "git+https://github.com/redhat-performance/opl.git#egg=opl-rhcloud-perf-team-extras&subdirectory=extras"

**Local Development:**

If you have cloned the git repository and want to develop locally, install the full package in editable mode:

    python -m pip install -e .[dev]

Running unit tests
------------------

    source venv/bin/activate
    python -m pytest tests/

Notes
------------------
* Our Jinja2 by default loads templates from the folder where the script `generic.py` is located.
  * If no template with a given name is found, the second option is used: the `/home/` folder. That's more useful for temporary changes. For example, if I have a template in iperf in `/home/compliance/mycustomtemplate.j2`, I'll omit the `/home` to use this: `compliance/mycustomtemplate.j2`.
