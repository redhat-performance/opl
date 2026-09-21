#!/usr/bin/env python3
"""Helpers for generating inventory account IDs."""

import random

import opl.db


def load_distinct_accounts(inventory_db_conf, d_dict):
    """
    Load all distinct account IDs from the inventory DB into d_dict.

    Each account ID is registered as a key with a True membership marker, so
    get_unique_key can avoid colliding with existing accounts.
    """
    query = "select distinct account from hosts;"
    data_list = opl.db.get_query_result(inventory_db_conf, query)
    if not data_list:
        raise RuntimeError("Failed to load distinct accounts from the inventory DB")
    for account in data_list:
        d_dict[account] = True

    return d_dict


def get_unique_key(d_dict):
    """
    Generate an account_id not present in d_dict and register it in d_dict
    so subsequent selections in the same run cannot collide with it.
    """
    while True:
        account_id = "".join([str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])) for _ in range(5)])
        if account_id not in d_dict:
            d_dict[account_id] = True
            return account_id
