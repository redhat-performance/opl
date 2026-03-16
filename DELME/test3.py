#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
