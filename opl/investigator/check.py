import logging
import statistics

import scipy.stats


def _check_by_stdev(data, value, trim=0.0):
    logging.debug(f"data={data} and value={value} and trim={trim}")
    mean = scipy.stats.trim_mean(data, trim)
    stdev = statistics.stdev(scipy.stats.trimboth(data, trim))
    lower_boundary = mean - stdev
    upper_boundary = mean + stdev
    logging.debug(f"{__name__}: value={value}, trim={trim:.03f}, data len={len(data)} mean={mean:.03f} and stdev={stdev:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}")
    return lower_boundary <= value <= upper_boundary


def check_by_stdev(data, value):
    return _check_by_stdev(data, value, trim=0)


def check_by_trim_stdev(data, value):
    return _check_by_stdev(data, value, trim=0.1)


def _check_by_error(data, value, boost=1.0):
    logging.debug(f"data={data} and value={value} and boost={boost}")
    mean = statistics.mean(data)
    error = statistics.mean([abs(i - mean) for i in data])
    lower_boundary = mean - error * boost
    upper_boundary = mean + error * boost
    logging.debug(f"{__name__}: value={value}, boost={boost}, data len={len(data)} mean={mean:.03f} and error={error:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}")
    return lower_boundary <= value <= upper_boundary


def check_by_error_1(data, value):
    return _check_by_error(data, value, 1)


def check_by_error_2(data, value):
    return _check_by_error(data, value, 2)


def check(data, value):
    ###methods = [check_by_trim_stdev, check_by_stdev, check_by_error_1, check_by_error_2]
    methods = [check_by_error_2]
    results = []
    for method in methods:
        result = method(data, value)
        results.append(result)
        logging.info(f"{method.__name__} value {value} returned {'PASS' if result else 'FAIL'}")
    return results
