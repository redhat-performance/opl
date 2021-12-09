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

`current:`
----------

This specifies from where we should load new (`current`) test result
we will be evaluating.

`sets:`
-------

This list status data paths (with numerical values) where it makes sense
to evaluate. E.g. you definitely want to include `results.rps` or
`measurements.cpu.mean`, but adding `parameters.test_started.timestamp`
might not be useful (because it does not represent test result comparable
across historical runs).

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
process. Every time we do some PASS/FAIL/ERROR decision, we record that
decision (it's parameters and result) into system defined here (e.g.
ElasticSearch index). That supports investigation of decision trends or so.
