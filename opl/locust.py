import copy
import logging
import re
import time

import gevent

import locust.env
import locust.log
import locust.stats

import tabulate


def run_locust(args, status_data, test_set, new_stats=False, summary_only=False):
    # Local runner is True by default, bot overwrite it if we have selected
    # master or worker runner
    assert not (
        args.locust_master_runner and args.locust_worker_runner
    ), "Either choose master or worker runner, not both"
    if args.locust_master_runner or args.locust_worker_runner:
        args.locust_local_runner = False

    # Additional opts, maybe put them into args someday
    args.master_port = 5557
    args.master_bind_host = "*"
    args.master_bind_port = 5557
    args.reset_stats = False

    # Add parameters to status data file
    status_data.set("parameters.locust.hatch_rate", args.hatch_rate)
    status_data.set("parameters.locust.host", args.host)
    status_data.set("parameters.locust.num_clients", args.num_clients)
    status_data.set("parameters.locust.reset_stats", args.reset_stats)
    status_data.set("parameters.locust.stop_timeout", args.stop_timeout)
    status_data.set("parameters.test.duration", args.test_duration)
    status_data.set("parameters.test.requests", args.test_requests)
    status_data.set("parameters.test.url_suffix", args.test_url_suffix)
    if "test_selection" in args:
        status_data.set("parameters.test.test_selection", args.test_selection)
    print(
        f"Running with host = {args.host}, num_clients = {args.num_clients}, hatch_rate = {args.hatch_rate}, duration = {args.test_duration} / requests = {args.test_requests}"
    )

    env = locust.env.Environment()
    env.user_classes = [test_set]
    env.stop_timeout = args.stop_timeout
    env.host = args.host
    env.reset_stats = args.reset_stats

    # Create runner and run test
    if args.locust_local_runner:

        env.create_local_runner()
        status_data.set("parameters.locust.runner", "local")

        # Start the test
        logging.info("Starting local Locust runner")
        status_data.set_now("parameters.start")
        env.runner.start(args.num_clients, spawn_rate=args.hatch_rate)

        # Wait (in some way) for a good time to quit the test
        if args.test_requests > 0:
            while True:
                num_requests = env.stats.num_requests
                if num_requests >= args.test_requests:
                    logging.debug(
                        f"Finished {num_requests} requests while requested number was {args.test_requests}"
                    )
                    break
                logging.debug(
                    f"Still waiting for test requests count ({num_requests} out of {args.test_requests})"
                )
                time.sleep(1)
        else:
            time.sleep(args.test_duration)
            logging.debug(f"Waited for {args.test_duration} seconds")
        gevent.spawn(lambda: env.runner.quit())

        # Wait for the greenlets to finish
        env.runner.greenlet.join()
        status_data.set_now("results.end")
        logging.info("Local Locust run finished")

        return show_locust_stats(env.stats, status_data, new_stats, summary_only)

    elif args.locust_master_runner:

        env.create_master_runner(
            master_bind_host=args.master_bind_host,
            master_bind_port=args.master_bind_port,
        )
        status_data.set("parameters.locust.runner", "master")
        status_data.set("parameters.locust.expect_workers", args.expect_workers)

        env.runner.spawn_rate = args.hatch_rate

        while len(env.runner.clients.ready) < args.expect_workers:
            logging.info(
                "Waiting for worker to become ready, %s of %s - %s",
                len(env.runner.clients.ready),
                args.expect_workers,
                ",".join([i.state for i in env.runner.clients.values()]),
            )
            time.sleep(1)

        # Start the test
        logging.info("Starting master Locust runer")
        status_data.set_now("parameters.start")
        env.runner.start(args.num_clients, spawn_rate=args.hatch_rate)

        # Wait configured time and quit the test
        time.sleep(args.test_duration)
        gevent.spawn(lambda: env.runner.quit())

        # Wait for the greenlets to finish
        env.runner.greenlet.join()
        status_data.set_now("results.end")
        logging.info("Master Locust run finished")

        return show_locust_stats(env.stats, status_data, new_stats, summary_only)

    elif args.locust_worker_runner:

        env.create_worker_runner(
            master_host=args.master_host,
            master_port=args.master_port,
        )
        status_data.set("parameters.locust.runner", "worker")
        status_data.set("parameters.locust.master_host", args.master_host)
        status_data.set("parameters.locust.master_port", args.master_port)

        # Start the test
        logging.info("Starting worker Locust runner")
        status_data.set_now("parameters.start")

        # Wait for the greenlets to finish
        env.runner.greenlet.join()
        status_data.set_now("results.end")
        logging.info("Worker Locust run finished")

    else:

        raise Exception("No runner specified")


def show_locust_stats(locust_stats, status_data, new_stats, summary_only):
    """
    Print Locust stats obejct and format nice table of it.
    Also add values to status data object.
    """

    # What is in `value` variable below:
    # ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_cache_response_times', '_log_response_time', '_log_time_of_request', 'avg_content_length', 'avg_response_time', 'current_fail_per_sec', 'current_rps', 'extend', 'fail_ratio', 'get_current_response_time_percentile', 'get_response_time_percentile', 'get_stripped_report', 'last_request_timestamp', 'log', 'log_error', 'max_response_time', 'median_response_time', 'method', 'min_response_time', 'name', 'num_fail_per_sec', 'num_failures', 'num_none_requests', 'num_reqs_per_sec', 'num_requests', 'percentile', 'reset', 'response_times', 'response_times_cache', 'serialize', 'start_time', 'stats', 'to_string', 'total_content_length', 'total_fail_per_sec', 'total_response_time', 'total_rps', 'unserialize', 'use_response_times_cache']

    # Format result table
    data = {
        "request": [],
        "count": [],
        "fail ratio": [],
        "med resp time": [],
        "avg content lenght": [],
        "total RPS": [],
    }
    data_new = {}

    # Load all rows
    sum_count = 0
    sum_failures = 0
    sum_total_response_time = 0.0
    sum_total_content_length = 0
    sum_total_rps = 0.0
    for name, value in locust_stats.entries.items():
        sum_count += value.num_requests
        sum_failures += value.num_failures
        sum_total_response_time += value.median_response_time * value.num_requests
        sum_total_content_length += value.total_content_length
        sum_total_rps += value.total_rps
        n = f"{name[1]} {name[0]}"
        if len(n) > 40:
            n = n[:39] + "…"
        data["request"].append(n)
        data["count"].append(value.num_requests)
        data["fail ratio"].append(value.fail_ratio)
        data["med resp time"].append(value.median_response_time)
        data["avg content lenght"].append(
            value.total_content_length / value.num_requests
        )
        data["total RPS"].append(value.total_rps)

        name_safe = re.sub("[^a-zA-Z0-9-]+", "_", f"{name[1]} {name[0]}")
        while name_safe in data_new:
            name_safe += "_"
        data_new[name_safe] = {
            "50percentile": value.get_response_time_percentile(0.50),
            "90percentile": value.get_response_time_percentile(0.90),
            "95percentile": value.get_response_time_percentile(0.95),
            "99percentile": value.get_response_time_percentile(0.99),
            "avg_content_length": value.avg_content_length,
            "avg_response_time": value.avg_response_time,
            "fail_ratio": value.fail_ratio,
            "max_response_time": value.max_response_time,
            "median_response_time": value.median_response_time,
            "min_response_time": value.min_response_time,
            "num_failures": value.num_failures,
            "num_none_requests": value.num_none_requests,
            "num_requests": value.num_requests,
            "total_rps": value.total_rps,
        }

    # Footer
    data["request"].append("SUMMARY")
    data_new["SUMMARY"] = {}
    data["count"].append(sum_count)
    data_new["SUMMARY"]["num_requests"] = sum_count
    data_new["SUMMARY"]["num_failures"] = sum_failures
    if sum_count != 0:
        data["fail ratio"].append(sum_failures / sum_count)
        data_new["SUMMARY"]["fail_ratio"] = sum_failures / sum_count
        data["med resp time"].append(sum_total_response_time / sum_count)
        data_new["SUMMARY"]["median_response_time"] = (
            sum_total_response_time / sum_count
        )
        data["avg content lenght"].append(sum_total_content_length / sum_count)
        data_new["SUMMARY"]["avg_content_length"] = sum_total_content_length / sum_count
    else:
        data["fail ratio"].append(None)
        data_new["SUMMARY"]["fail_ratio"] = None
        data["med resp time"].append(None)
        data_new["SUMMARY"]["median_response_time"] = None
        data["avg content lenght"].append(None)
        data_new["SUMMARY"]["avg_content_length"] = None
    data_new["SUMMARY"]["total_content_length"] = sum_total_content_length
    data["total RPS"].append(sum_total_rps)
    data_new["SUMMARY"]["total_rps"] = sum_total_rps

    # Print table
    print(tabulate.tabulate(data, headers="keys", floatfmt=".3f"))

    print("Errors encountered:")
    errors = list(locust_stats.serialize_errors().values())
    if len(errors) == 0:
        print("Good, no errors.")
    else:
        errors_table = [
            e.update({"error": e["error"][:100]}) or e for e in copy.deepcopy(errors)
        ]
        table = tabulate.tabulate(errors_table, headers="keys")
        print(table)
    if status_data is not None:
        logging.debug("Adding errors to status data file")
        status_data.set("results.errors", errors)

    if not new_stats:
        # Add results to status data file
        transposed = {}
        for i in range(len(data["request"])):
            r_req = data["request"][i]
            r_status = "OK" if data["fail ratio"][i] == 0.0 else "EE"
            r = f"[{r_status}] {r_req}"
            if r in transposed:
                logging.error(
                    "Second same key? That is strange. We are loosing data in status data file."
                )
            transposed[r] = {}
            for f in ["count", "fail ratio", "med resp time", "total RPS"]:
                transposed[r][f] = data[f][i]
            sd_data = transposed
    else:
        if summary_only:
            sd_data = {k: v for k, v in data_new.items() if k == "SUMMARY"}
        else:
            sd_data = data_new

    if status_data is not None:
        logging.debug(
            f"Adding {'new' if new_stats else 'old'} style results to status data file"
        )
        status_data.set("results.requests", sd_data)

    return sum_failures
