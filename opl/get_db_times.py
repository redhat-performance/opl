#!/usr/bin/env python3

import argparse
import datetime
import logging
import threading
import time

import opl.args
import opl.data
import opl.db
import opl.skelet

import psycopg2
import psycopg2.extras

import yaml


"""
You want to use this helper if you want to get timestamps on when your
hosts landed in application DB and store these timestamps in storage DB.

To create a script using this helper, you can create this:

    import opl.args
    import opl.get_db_times


    def func_add_more_args(parser):
        opl.args.add_edge_db_opts(parser)


    def func_create_app_db_config(args):
        return {
            'host': args.edge_db_host,
            'port': args.edge_db_port,
            'database': args.edge_db_name,
            'user': args.edge_db_user,
            'password': args.edge_db_pass,
        }


    if __name__ == "__main__":
        config = {
            "func_add_more_args": func_add_more_args,
            "func_create_app_db_config": func_create_app_db_config,
            "query_storage_update_timestamp": "query_storage_update_created_at",   # update query to store created_at into items table
            "query_storage_count_applicable_hosts": "query_storage_count_applicable_hosts",   # query to get count of hosts with missing created_at value
            "query_storage_get_applicable_hosts": "query_storage_get_applicable_hosts",   # query to get IDs of hosts with missing created_at value
            "query_app_get_hosts": "query_edge_get_created_at",   # query host ID and created_at from Edge DB for given hosts
        }
        opl.get_db_times.get_db_times(config)

And have something like this in your tables.yaml:

    tables:
        items:
            - CREATE TABLE IF NOT EXISTS items (
                  subscription_manager_id VARCHAR PRIMARY KEY,
                  qpc_at TIMESTAMP WITH TIME ZONE NULL,
                  created_at TIMESTAMP WITH TIME ZONE NULL)
            - CREATE INDEX IF NOT EXISTS items_subscription_manager_id_idx
                  ON items (subscription_manager_id)
    queries:
        query_storage_update_created_at: UPDATE items SET created_at = data.created_at FROM (VALUES %s) AS data(subscription_manager_id, created_at) WHERE items.subscription_manager_id = data.subscription_manager_id
        query_storage_count_applicable_hosts: SELECT COUNT(*) FROM items WHERE qpc_at IS NOT NULL AND created_at IS NULL
        query_storage_get_applicable_hosts: SELECT subscription_manager_id FROM items WHERE qpc_at IS NOT NULL AND created_at IS NULL OFFSET %s LIMIT %s
        query_edge_get_created_at: SELECT uuid, created_at FROM devices WHERE uuid=ANY(%s)
"""


class GetDbTimes:
    """
    This class is meant to encapsulate getting timestamps for given host IDs
    gtom application DB and recording them in storage DB
    """

    def __init__(self, args, status_data, config):
        """
        Connect to the storage DB and app DB, load SQL query templates
        and initiate a BatchProcessor.
        """
        self.args = args
        self.status_data = status_data
        self.config = config

        # Sanitize (mostly just get rid of passwords) and include args into
        # status data file
        args_copy = vars(args).copy()
        args_copy["tables_definition"] = args_copy["tables_definition"].name
        for k in list(args_copy.keys()):
            if k.endswith("_db_pass"):
                del args_copy[k]
        self.status_data.set("parameters.get_db_times", args_copy)

        # Open a connection to Storage DB
        storage_db_conf = {
            "host": args.storage_db_host,
            "port": args.storage_db_port,
            "database": args.storage_db_name,
            "user": args.storage_db_user,
            "password": args.storage_db_pass,
        }
        self.storage_db = psycopg2.connect(**storage_db_conf)

        # Open connection to application DB
        app_db_conf = config["func_create_app_db_config"](args)
        self.app_db = psycopg2.connect(**app_db_conf)

        # Load queries
        self.queries_definition = yaml.load(
            args.tables_definition, Loader=yaml.SafeLoader
        )["queries"]

        # Create object to make it easy to add timestamps to storage DB
        sql = self.queries_definition[self.config["query_storage_update_timestamp"]]
        logging.info(f"Creating storage DB batch inserter with {sql}")
        data_lock = threading.Lock()
        self.save_here = opl.db.BatchProcessor(
            self.storage_db, sql, batch=100, lock=data_lock
        )

        # When was the last host added to storage DB - initializing to now
        self.last_added = self.dt_now()
        # If there is no host added for this long, give up
        self.activity_timeout = args.activity_timeout

    def dt_now(self):
        """
        Return current time in UTC timezone with UTC timezone.
        """
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    def _storage_count_applicable_hosts(self):
        """
        Count hosts in storage DB that have empty target timestamp column.
        """
        cursor = self.storage_db.cursor()
        sql = self.queries_definition[
            self.config["query_storage_count_applicable_hosts"]
        ]
        cursor.execute(sql)
        count = int(cursor.fetchone()[0])
        cursor.close()
        logging.debug(f"There are {count} applicable hosts")
        return count

    def _storage_get_applicable_hosts(self, batch_counter, batch_size):
        """
        Get batch of hosts IDs from storage DB that still have empty target
        column. You need to provide batch number and batch size.
        """
        batch_offset = batch_counter * batch_size
        cursor = self.storage_db.cursor()
        sql = self.queries_definition[self.config["query_storage_get_applicable_hosts"]]
        cursor.execute(sql, (batch_offset, batch_size))
        hosts = [h[0] for h in cursor.fetchall()]
        cursor.close()
        logging.debug(
            f"Going to process batch {batch_counter} of hosts on offset {batch_offset} and limit {batch_size}: {', '.join(hosts)[:50]}..."
        )
        return hosts

    def _app_get_hosts(self, batch_hosts):
        """
        For given host IDs, gather (host_id, timestamp) rows from
        application DB.
        """
        cursor = self.app_db.cursor()
        sql = self.queries_definition[self.config["query_app_get_hosts"]]
        cursor.execute(sql, (batch_hosts,))
        timestamps = cursor.fetchall()
        cursor.close()
        logging.debug(f"Gathered {len(timestamps)} timestamps for the hosts")
        return timestamps

    def work(self):
        """
        1. Get host IDs from storage DB
        2. Get timetamp from app DB
        3. Store timestamps in storage DB
        4. Go to 1. until we have all hosts with their timestamps
        """
        batch_size = 100

        while True:
            # Number of batches in which we will be processing remaining hosts
            batch_count = int(self._storage_count_applicable_hosts() / batch_size) + 1

            # Process (by batches) all hosts
            for batch_counter in range(batch_count):
                batch_hosts = self._storage_get_applicable_hosts(
                    batch_counter, batch_size
                )

                timestamps = self._app_get_hosts(batch_hosts)

                for row in timestamps:
                    self.save_here.add(row)
                    self.last_added = self.dt_now()

                delay = self.dt_now() - self.last_added
                if delay.total_seconds() > self.activity_timeout:
                    self.save_here.commit()
                    raise Exception(
                        f"No new host added for too long ({delay}), giving up"
                    )

            if self._storage_count_applicable_hosts() == 0:
                logging.debug("All hosts processes")
                break
            else:
                logging.debug("Waiting so more hosts can be processed")
                time.sleep(10)


def get_db_times(config):
    """
    This is the main helper function you should use in your code.
    It handles arguments, opening status data file and running
    the actual workload.
    """
    parser = argparse.ArgumentParser(
        description="Read timestaps for given hosts form application DB and store it into storage DB",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--activity-timeout",
        type=int,
        default=180,
        help="If there is new host for this many seconds, quit with error",
    )
    opl.args.add_storage_db_opts(parser)
    opl.args.add_tables_def_opts(parser)

    # GetDbTimes needs this config keys in config dict
    assert "func_add_more_args" in config
    assert "func_create_app_db_config" in config
    assert "query_storage_update_timestamp" in config
    assert "query_storage_update_timestamp" in config
    assert "query_storage_get_applicable_hosts" in config
    assert "query_storage_get_applicable_hosts" in config

    # Add more args
    config["func_add_more_args"](parser)

    with opl.skelet.test_setup(parser) as (args, status_data):
        get_db_times_object = GetDbTimes(
            args,
            status_data,
            config,
        )
        get_db_times_object.work()
