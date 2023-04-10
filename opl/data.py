import datetime
import logging
import statistics
import time
import numpy


class WaitForDataAndSave:
    def __init__(self, data_db, storage_db, queries, save_here):
        self.data_db = data_db
        self.storage_db = storage_db
        self.queries = queries
        self.save_here = save_here
        self.batch_size = 100
        self.expected_count = self._get_expected_count()

    def _get_expected_count(self):
        cursor = self.storage_db.cursor()
        sql = self.queries["get_expected_count"]
        cursor.execute(sql)
        return int(cursor.fetchone()[0])

    def _get_remaining_count(self):
        cursor = self.storage_db.cursor()
        sql = self.queries["get_remaining_count"]
        cursor.execute(sql)
        return int(cursor.fetchone()[0])

    def _get_remaining(self, batch_number):
        cursor = self.storage_db.cursor()
        sql = self.queries["get_remaining"]
        cursor.execute(sql, (self.batch_size, batch_number * self.batch_size))
        return tuple([row[0] for row in cursor.fetchall()])

    def _check_these(self, batch):
        count = 0
        logging.debug(f"Checking these: {','.join(batch[:3])}... ({len(batch)} total)")
        if len(batch) == 0:
            return 0
        data_cursor = self.data_db.cursor()
        sql = self.queries["read_these"]
        data_cursor.execute(sql, (batch,))
        for row in data_cursor.fetchall():
            logging.debug(f"Saving row {row}")
            self.save_here.add(row)
            count += 1
        return count

    def wait_common_db_change(self):
        """
        It might take some time before finished messages lands in data DB,
        so wait for some change (without checking that change we see is for
        some system in question). If query returns 0, it is also indication
        we are ready to go.
        """

        logging.debug("Waiting for some change in the DB")
        count_old = None
        data_cursor = self.data_db.cursor()
        sql = self.queries["get_all_done_count"]
        while True:
            data_cursor.execute(sql)
            count = data_cursor.fetchone()[0]

            # This is first pass through the loop
            if count_old is None:
                count_old = count
                time.sleep(10)
                continue

            # Finally, there was a change

            if count == 0:
                logging.info(
                    f"Finally, count is {count} (was {count_old}), so we can go on"
                )
                break

            if count != count_old:
                logging.info(f"Finally, count {count_old} changed to {count}")
                break

            # Wait some more
            logging.debug(f"Count is still only {count}, waiting")
            count_old = count
            time.sleep(10)

    def process(self):
        logging.debug(f"Going to process {self.expected_count} items")
        iteration = 0
        iteration_wait = 10
        batch_wait = 0.1
        found_in_total = 0
        found_recently = [
            1
        ]  # track how many items we have found in <found_recently_size> iterations - seed with fake 1, so we do not exit at first pass
        found_recently_size = 100
        while True:
            found_in_iteration = 0
            remaining = self._get_remaining_count()
            batches_count = int(remaining / self.batch_size) + 1
            logging.debug(
                f"Iteration {iteration} running with {batches_count} batches for {remaining} remaining items"
            )

            # Go through all remaining values (from storage DB) in batches
            # and attempt to get dates from data DB
            for batch_number in range(batches_count):
                batch = self._get_remaining(batch_number)
                found_count = self._check_these(batch)
                logging.debug(
                    f"In iteration {iteration} batch {batch_number} we have found {found_count} new items"
                )
                found_in_iteration += found_count
                time.sleep(batch_wait)

            # Detect cases when we have not found any new items for too long
            found_recently.append(found_in_iteration)
            while len(found_recently) > found_recently_size:
                found_recently.pop(0)
            if sum(found_recently) == 0:
                raise Exception(
                    f"Nothing found in last {len(found_recently)} iterations, giving up"
                )

            # Are we done?
            if remaining == found_in_iteration:
                logging.info(
                    f"We are done in iteration {iteration} with all {self.expected_count} items"
                )
                found_in_total += found_in_iteration
                break

            iteration += 1
            found_in_total += found_in_iteration
            time.sleep(iteration_wait)

        return found_in_total


def data_stats(data):
    if len(data) == 0:
        return {"samples": 0}
    non_zero_data = [i for i in data if i != 0]
    if isinstance(data[0], int) or isinstance(data[0], float):
        q25 = numpy.percentile(data, 25)
        q75 = numpy.percentile(data, 75)
        q90 = numpy.percentile(data, 90)
        q99 = numpy.percentile(data, 99)
        q999 = numpy.percentile(data, 99.9)
        return {
            "samples": len(data),
            "min": min(data),
            "max": max(data),
            "sum": sum(data),
            "mean": statistics.mean(data),
            "non_zero_mean": statistics.mean(non_zero_data)
            if len(non_zero_data) > 0
            else 0.0,
            "median": statistics.median(data),
            "non_zero_median": statistics.median(non_zero_data)
            if len(non_zero_data) > 0
            else 0.0,
            "stdev": statistics.stdev(data) if len(data) > 1 else 0.0,
            "range": max(data) - min(data),
            "percentile25": q25,
            "percentile75": q75,
            "percentile90": q90,
            "percentile99": q99,
            "percentile999": q999,
            "iqr": q75 - q25,
        }
    elif isinstance(data[0], datetime.datetime):
        return {
            "samples": len(data),
            "min": min(data),
            "max": max(data),
            "mean": (max(data) - min(data)) / len(data),
            "range": max(data) - min(data),
        }
    else:
        raise Exception(f"Do not know how to get stats for list of {type(data[0])}")


def get_hist(data):
    hist_counts, hist_borders = numpy.histogram(data)
    hist_counts = [float(i) for i in hist_counts]
    hist_borders = [float(i) for i in hist_borders]
    out = []
    for i in range(len(hist_counts)):
        out.append(((hist_borders[i], hist_borders[i + 1]), hist_counts[i]))
    return out


def visualize_hist(data):
    for i in get_hist(data):
        print(f"<{i[0][0]:.2f}, {i[0][1]:.2f})\t: {i[1]}")


def get_rps(data, bucket_size=None, granularity=None):
    """
    For given list of timestamps "data", count RPS values "bucket_size"
    long interval floating across data (this is set to 10 by default
    to stabilize data a bit, but you can set to 1)
    """
    if len(data) == 0:
        return []

    out = []
    data_max = max(data)
    bucket_start = min(data)
    if bucket_size is None:
        bucket_size = (data_max - bucket_start) / 30
        bucket_size = max(bucket_size, 10)
    if granularity is None:
        granularity = bucket_size / 5
        granularity = max(granularity, 1)
    bucket_end = bucket_start + bucket_size
    logging.debug(
        "Counting RPS for %d data points with min %d and max %d with bucket_size=%d and granularity=%d",
        len(data),
        bucket_start,
        data_max,
        bucket_size,
        granularity,
    )

    while bucket_start <= data_max:
        bucket = [i for i in data if bucket_start <= i < bucket_end]

        # If this is last interval, only consider actual length of
        # the interval, also check for special case case
        if len(bucket) == 1 and bucket[0] == bucket_start:
            bucket_duration = 1
        elif bucket_end > data_max:
            bucket_duration = max(bucket) - bucket_start + 1
        else:
            bucket_duration = bucket_size

        try:
            rps = len(bucket) / bucket_duration
        except ZeroDivisionError:
            logging.warning(
                "Empty bucket %s - %s when counting RPS", bucket_start, bucket_end
            )

            out.append(0)
        else:
            out.append(rps)

        bucket_start += granularity
        bucket_end += granularity

    return out
