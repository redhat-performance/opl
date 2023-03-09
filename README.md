MBU products perf&scale library
======================

OPL library
-----------

Contains various helpers for not only RHCloud performance testing.

Generic command-line tools
--------------------------

There is couple of tools used mostly to integrate with CPT and comp.:

* `cluster_read.py` - Library (and command-line tool) to get data in a ways
  defined in a config file. It can execute command, read from Prometheus or
  Grafana. It is used by `status_data.py` to enritch status data files with
  facts (as defined in per-test config file). Usually it is info about
  the cluster (using `oc ... | jq ...` commands) or monitoring data from
  Prometheus. E.g. see `opl/cluster_read_example.yaml`.
* `pass_or_fail.py` - Tool which uses simple statistic in an attempt to
  decide if latest test result is PASS or FAIL when compared to historical
  results. Example of the config file is in
  `opl/investigator/sample_config.yaml`.
* `junit_cli.py` - Script to manipulate JUnit XML file from CLI. It is
  used by Satellite CPT.
* `status_data.py` - Library (and command-line tool) to manipulate status
  data files.
* `status_data_report.py` - Tool to render Jinja2 template with data from
  status data file. It is used by tests to provide final summary without need
  to write per-test tool which would do it - Jinja2 template seems to provide
  enough logick for what is needed in the output. Each test have its own
  template - e.g. see `opl/status_data_report.txt`.
* `status_data_diff.py` - Convenience tool to show differences in two status
  data files.

These tools are only used by tests:

* `script-skip-to-end.py` - Script to skip to the end of Kafka queues for
  given consumer group (it should be trivial given python-kafka docs, but
  simplest way did not worked for me)
* `script-manage-db.py` - Helper script to manipulate with utility DB.
  Consumes config with list of tables relevant for given test and SQL needed
  to create them. E.g. see `opl/sample-tables.yaml`

Installation
------------

Install with:

    python -m venv venv
    source venv/bin/activate
    python -m pip install git+https://github.com/redhat-performance/opl.git

If you have cloned the git and want to develop locally, replace last step with:

    python -m pip install --editable .

Running unit tests
------------------

    source venv/bin/activate
    python -m pytest

Notes
------------------
* Our Jinja2 by default loads templates from the folder where the script `generic.py` is located.
  * If no template with a given name is found, the second option is used: the `/home/` folder. That's more useful for temporary changes. For example, if I have a template in iperf in `/home/compliance/mycustomtemplate.j2`, I'll omit the `/home` to use this: `compliance/mycustomtemplate.j2`.
