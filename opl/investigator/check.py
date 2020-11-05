import inspect
import logging
import statistics
import collections

import scipy.stats


def _check_by_stdev(data, value, trim=0.0, boost=1.0):
    logging.debug(f"data={data} and value={value} and trim={trim} and boost={boost}")
    mean = scipy.stats.trim_mean(data, trim)
    stdev = statistics.stdev(scipy.stats.trimboth(data, trim))
    lower_boundary = mean - stdev * boost
    upper_boundary = mean + stdev * boost
    logging.info(f"value={value}, trim={trim:.03f}, boost={boost:.03f}, data len={len(data)} mean={mean:.03f} stdev={stdev:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}")
    info = collections.OrderedDict([
        ("method", inspect.stack()[1][3]),
        ("value", value),
        ("trim", trim),
        ("boost", boost),
        ("data len", len(data)),
        ("data mean", mean),
        ("data svdev", stdev),
        ("lower_boundary", lower_boundary),
        ("upper_boundary", upper_boundary),
    ])
    return lower_boundary <= value <= upper_boundary, info


def check_by_stdev(data, value):
    return _check_by_stdev(data, value, trim=0)


def check_by_stdev_2(data, value):
    return _check_by_stdev(data, value, trim=0, boost=2)


def check_by_trim_stdev(data, value):
    return _check_by_stdev(data, value, trim=0.1)


def check_by_trim_stdev_2(data, value):
    return _check_by_stdev(data, value, trim=0.1, boost=2)


def _check_by_error(data, value, boost=1.0):
    logging.debug(f"data={data} and value={value} and boost={boost}")
    mean = statistics.mean(data)
    error = statistics.mean([abs(i - mean) for i in data])
    lower_boundary = mean - error * boost
    upper_boundary = mean + error * boost
    logging.info(f"value={value}, boost={boost}, data len={len(data)} mean={mean:.03f} and error={error:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}")
    info = collections.OrderedDict([
        ("method", inspect.stack()[1][3]),
        ("value", value),
        ("boost", boost),
        ("data len", len(data)),
        ("data mean", mean),
        ("data error", error),
        ("lower_boundary", lower_boundary),
        ("upper_boundary", upper_boundary),
    ])
    return lower_boundary <= value <= upper_boundary, info


def check_by_error_1(data, value):
    return _check_by_error(data, value, 1)


def check_by_error_2(data, value):
    return _check_by_error(data, value, 2)


def check_by_error_3(data, value):
    return _check_by_error(data, value, 3)


def _check_by_perc(data, value, perc=20):
    logging.debug(f"data={data} and value={value} and perf={perc}")
    mean = statistics.mean(data)
    lower_boundary = mean - mean * (perc / 100 / 2)
    upper_boundary = mean + mean * (perc / 100 / 2)
    logging.info(f"value={value}, perc={perc}, data len={len(data)} mean={mean:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}")
    info = collections.OrderedDict([
        ("method", inspect.stack()[1][3]),
        ("value", value),
        ("perc", perc),
        ("data len", len(data)),
        ("data mean", mean),
        ("lower_boundary", lower_boundary),
        ("upper_boundary", upper_boundary),
    ])
    return lower_boundary <= value <= upper_boundary, info


def check_by_perc_40(data, value):
    return _check_by_perc(data, value, perc=40)


def check_by_perc_60(data, value):
    return _check_by_perc(data, value, perc=60)


def check_by_perc_100(data, value):
    return _check_by_perc(data, value, perc=60)


def _check_by_min_max(data, value, trim=0, boost=1.0):
    logging.debug(f"data={data} and value={value} and trim={trim} and boost={boost}")
    mean = statistics.mean(data)
    data_trimmed = scipy.stats.trimboth(data, trim)
    lower_boundary = min(data_trimmed)
    upper_boundary = max(data_trimmed)
    logging.info(f"value={value}, trim={trim}, boost={boost}, data len={len(data)} mean={mean:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}")
    info = collections.OrderedDict([
        ("method", inspect.stack()[1][3]),
        ("value", value),
        ("trim", trim),
        ("boost", boost),
        ("data len", len(data)),
        ("data mean", mean),
        ("lower_boundary", lower_boundary),
        ("upper_boundary", upper_boundary),
    ])
    return lower_boundary <= value <= upper_boundary, info


def check_by_min_max_7_1(data, value):
    return _check_by_min_max(data, value, trim=0.07, boost=1)


def check(data, value, description="N/A", verbose=True):
    ###methods = [check_by_trim_stdev, check_by_stdev, check_by_error_1, check_by_error_2]
    methods = [check_by_stdev_2, check_by_error_3, check_by_perc_100, check_by_min_max_7_1]
    results = []
    info_all = []
    for method in methods:
        result, info = method(data, value)
        results.append(result)
        logging.info(f"{method.__name__} value {value} returned {'PASS' if result else 'FAIL'}")

        info_full = collections.OrderedDict()
        info_full['description'] = description
        info_full['result'] = 'PASS' if result else 'FAIL'
        info_full.update(info)
        info_all.append(info_full)
    return results, info_all
