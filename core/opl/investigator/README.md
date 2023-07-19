Results investigator
====================

This tool (see `../pass_or_fail.py` in one level up directory) is supposed
to check historical results of some given test, compare with new result
and decide if new test result is PASS or FAIL.

See `sample_config.yaml` for example configuration. This is what each
section is for:

`history:`
----------

This specifies from where we should get historical data. Sample config
uses ElasticSearch plugin to retrieve it. Most important part here is
`es_query` which is described in ElasticSearch docs:

    https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html

This query is used to only filter documents that are useful to us:
we only want documents for same test (you can use status data field
`name`) which were running with same parameters and so on.

That query is Jinja2 template-able, so you can include:

    - term:
        parameters.cluster.pods.yupana.count: "{{ current.get('parameters.cluster.pods.yupana.count') }}"

to dynamically obtain the value from new result and use it to filter for
historical results.

There are other plugins you can use to retrieve distorical data:

 * `elasticsearch` - Retrieves historical data from ElasticSearch
   and is described above

 * `csv` - CSV file with rows being historical results and columns
   individual data sets. Example of a CSV file:

    id,name,results.duration
    run-2022-01-07T20:57:40+00:00,Test XYZ,152
    run-2022-01-08T03:01:07+00:00,Test XYZ,148
    run-2022-01-08T22:16:30+00:00,Test XYZ,155
    run-2022-01-09T04:20:04+00:00,Test XYZ,151
    run-2022-01-11T01:16:47+00:00,Test XYZ,144

 * `sd_dir` - directory with status data files from past experiments
   which allows filtering by matching various fields before loading data.
   Below is example where we load data from SD files whose `name` matches
   `name` value from current result. `matchers` is Jinja2 template again:

    type: sd_dir
    dir: /tmp/historical_sd_storage/
    matchers: |
      name: "{{ current.get('name') }}"


`current:`
----------

This specifies from where we should load new (`current`) test result
we will be evaluating.

There is only choice now that loads current result from status data file.

This can be overwriten by `--current-file` command line option.


`methods:`
----------

Alows you to specify list of checks you want to use to check results.
These checks are defined in `check.py`. Impractical example:

    methods:
      - check_by_stdev_1
      - check_by_stdev_2
      - check_by_stdev_3
      - check_by_trim_stdev_1
      - check_by_trim_stdev_2
      - check_by_error_1
      - check_by_error_2
      - check_by_error_3
      - check_by_error_4
      - check_by_error_5
      - check_by_perc_20
      - check_by_perc_40
      - check_by_perc_60
      - check_by_perc_80
      - check_by_perc_100
      - check_by_min_max_7_1
      - check_by_min_max_7_2
      - check_by_min_max_7_3

This is optional and if not present or empty, default set of checks will
be used.


`sets:`
-------

This list status data paths (with *numerical* values) where it makes sense
to evaluate. E.g. you definitely want to include something like `results.rps`
or `measurements.cpu.mean`, but adding `parameters.test_started.timestamp`
might not be useful (because it does not represent test result comparable
across historical runs - this timestamp is simply always different, based
on when the test was running, so it does not make sense to compare it
across historical results).

If this is not a list but a string like in the example below, it is first
rendered via Jinja2 and only then parsed as YAML to get the final list:

    sets: |
      {% if current.get('parameters.cli').startswith('experiment/reg-average.py ') %}
      - results.items.avg_duration
      {% else %}
      - results.duration
      {% endif %}
      - measurements.satellite.swap.swap-used.mean


`decisions:`
------------

This is optional and serves to record internal stats about evaluation
process. Every time we do some PASS/FAIL/ERROR decision on any metric
(as defined in `sets`), we record that decision (it's parameters and
result) into system defined here.

As of now you can use these decisions storage plugins:

 * `elasticsearch` - stores decisions to ElasticSearch index. Then in
   Kibana you can have investigation of decision trends dashboards or so.
 * `csv` - stores all the decisions for current test in a CSV file
   (overwritten every time the tool is invoked)

This can be turned off with `--dry-run` command line option.
