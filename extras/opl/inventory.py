#!/usr/bin/env python3
import random

import opl.db


def load_distinct_accounts(inventory_db_conf, d_dict):
    """
    load_distinct_accounts loads all the distinct accounts from the database.
    """
    query = "select distinct account from hosts;"
    # TODO: loading distinct accounts into d_dict is not implemented; the
    # statement was a no-op subscript read, removed to satisfy pylint W0104.
    opl.db.get_query_result(inventory_db_conf, query)

    return d_dict


def get_unique_key(d_dict):
    """
    get_unique_key generates an account_id which is not present in the input d_dict
    """
    tracker = False
    while not tracker:
        account_id = "".join(
            [str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])) for _ in range(5)]
        )
        if account_id not in d_dict:
            # TODO: registering the new key was a no-op statement; verify intent
            tracker = True

    return account_id
