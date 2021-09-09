#!/usr/bin/env python3

# Basic setup for subsequent code
import requests
import uuid
import os.path
import logging
import random
import psycopg2
import sys
import argparse
import datetime
import time

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import opl.args   # noqa: E402
import opl.skelet   # noqa: E402
import opl.gen   # noqa: E402
import opl.rbac_utils   # noqa: E402

APPLICATIONS = []
PERMISSIONS = []

errors_counter = 0


def _get_user():
    return 'user-' + str(uuid.uuid4())


def _get_access():
    return random.choice(PERMISSIONS)


def _get_group():
    name = 'group-' + str(uuid.uuid4())
    return {
      "name": name,
      "description": f"Test group {name}",
    }


def _get_role():
    name = "role-" + str(uuid.uuid4())
    return {
       "name": name,
       "description": f"Test role {name}",
       "access": [
            {
                "permission": _get_access(),
                "resourceDefinitions": [],
            },
        ],
    }


def _run_request(func, *args, **kwargs):
    global errors_counter
    max_attempts = 30
    sleep = 10
    attempt = 0
    while True:
        response = func(*args, **kwargs)
        try:
            _check_response(response)
        except requests.exceptions.HTTPError:
            if attempt <= max_attempts:
                logging.warning(f"Waiting to try again, attempt {attempt} of {max_attempts}")
                time.sleep(sleep)
                attempt += 1
                errors_counter += 1
                continue
            else:
                raise
        else:
            return response


def _check_response(response):
    if not response.ok:
        logging.error(f"Request failed with {response.content}")
    response.raise_for_status()


def load_apps_and_perms(url_base, x_rh_identity, application=[]):
    global APPLICATIONS
    global PERMISSIONS

    url = f"{url_base}/permissions/"
    headers = {
        'X_RH_IDENTITY': x_rh_identity,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    params = {
        'limit': 1000,
    }
    logging.info(f"Loading applications and permissions with identity header {x_rh_identity}")
    r = _run_request(requests.get, url, params=params, headers=headers, verify=False)

    for i in r.json()["data"]:
        if i["application"] in application:
            PERMISSIONS.append(i["permission"])
    
    APPLICATIONS = application.copy()
    assert len(PERMISSIONS) > 0
    assert len(APPLICATIONS) > 0


def create_tenant(url_base, x_rh_identity):
    # Because we are behind 3Scale => we are authenticated and every request
    # with unknown account will create new tenant for it
    url = f"{url_base}/roles/"
    headers = {
        'X_RH_IDENTITY': x_rh_identity,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    logging.info(f"Creating tenant with identity header {x_rh_identity}")
    _run_request(requests.get, url, headers=headers, verify=False)


def create_group(url_base, x_rh_identity):
    url = f"{url_base}/groups/"
    headers = {
        'X_RH_IDENTITY': x_rh_identity,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = _get_group()
    logging.info(f"Creating group name = {data['name']}")
    response = _run_request(requests.post, url, headers=headers, verify=False, json=data)
    return response.json()['uuid']


def create_role(url_base, x_rh_identity):
    url = f"{url_base}/roles/"
    headers = {
        'X_RH_IDENTITY': x_rh_identity,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = _get_role()
    logging.info(f"Creating role name = {data['name']}")
    response = _run_request(requests.post, url, headers=headers, verify=False, json=data)
    return response.json()['uuid']


def add_roles_to_group(url_base, x_rh_identity, role_list, group_uuid):
    url = f"{url_base}/groups/{group_uuid}/roles/"
    headers = {
        'X_RH_IDENTITY': x_rh_identity,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {"roles": role_list}
    logging.info(f"Adding roles = {role_list} to group = {group_uuid}")
    _run_request(requests.post, url, headers=headers, verify=False, json=data)


def create_principal(cursor):
    user_uuid = str(uuid.uuid4())
    user_name = "user-" + user_uuid
    logging.info(f"Creating principal username = {user_name}")
    cursor.execute("INSERT INTO management_principal (uuid, username) VALUES (%s, %s) RETURNING id", (user_uuid, user_name))
    user_id = cursor.fetchone()[0]
    return user_name, user_id


def add_principal_to_group(cursor, user_id, group_uuid):
    logging.info(f"Adding principal {user_id} to group {group_uuid}")
    cursor.execute("SELECT id FROM management_group WHERE uuid = %s", (group_uuid,))
    group_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO management_group_principals (group_id, principal_id) VALUES (%s, %s)", (group_id, user_id))


def doit(rbac_test_data, args, status_data):
    url_base = f"{args.rbac_host}{args.rbac_url_suffix}"

    global errors_counter

    tenant_counter = 0
    group_counter = 0
    role_counter = 0
    principal_counter = 0

    population_start = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    for _ in range(args.tenants_number):
        # Create identity header for this tenant
        account = opl.gen.gen_account()
        user = _get_user()
        logging.info(f"Creating tenant account = {account} and user = {user}")
        x_rh_identity = opl.gen.get_auth_header(account, user)

        # Load applications and permissions to work with
        if tenant_counter == 0:
            load_apps_and_perms(url_base, x_rh_identity, args.application)

        # Create tenant   POST /roles/
        create_tenant(url_base, x_rh_identity)

        # Add new tenant to test data
        rbac_test_data.add_account(account, [], APPLICATIONS)

        tenant_counter += 1
        principal_counter += 1

        # Create groups   POST /groups/
        group_list = []
        for _ in range(args.groups_number):
            group_uuid = create_group(url_base, x_rh_identity)
            group_list.append(group_uuid)

            group_counter += 1

            # Create roles   POST /roles/
            role_list = []
            for _ in range(args.roles_number):
                role_uuid = create_role(url_base, x_rh_identity)
                role_list.append(role_uuid)

                role_counter += 1

            # Add roles to the group   POST /groups/{group_uuid}/roles
            add_roles_to_group(url_base, x_rh_identity, role_list, group_uuid)

        rbac_db_conf = {
            'host': args.rbac_db_host,
            'port': args.rbac_db_port,
            'database': args.rbac_db_name,
            'user': args.rbac_db_user,
            'password': args.rbac_db_pass,
        }
        logging.info(f"Connecting to DB: {rbac_db_conf}")
        connection = psycopg2.connect(**rbac_db_conf)
        cursor = connection.cursor()
        cursor.execute(f"SET search_path TO acct{account}")

        # Create users   (via SQL for now because of https://projects.engineering.redhat.com/browse/RHIOPS-557)
        for _ in range(args.principals_number):
            user_name, user_id = create_principal(cursor)
            for group_uuid in group_list:
                add_principal_to_group(cursor, user_id, group_uuid)

            # Add new user to test data   (via SQL for now because of https://projects.engineering.redhat.com/browse/RHIOPS-557)
            rbac_test_data.add_account(account, [user_name], [])

            principal_counter += 1

        connection.commit()

    # TODO: Create ticket to e2e-deploy about development: false for perf env

    population_end = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    # rbac_test_data.save()

    print(f"DB population finished in {(population_end - population_start).total_seconds()} seconds")
    print(f"Tenants created: {tenant_counter}")
    print(f"Groups created: {group_counter}")
    print(f"Roles created: {role_counter}")
    print(f"Principals created: {principal_counter}")
    print(f"Errors encountered: {errors_counter}")

    status_data.set('parameters.test.data_created.end', population_end)
    status_data.set('parameters.test.data_created.start', population_start)
    status_data.set('parameters.test.data_created.tenant_counter', tenant_counter)
    status_data.set('parameters.test.data_created.group_counter', group_counter)
    status_data.set('parameters.test.data_created.role_counter', role_counter)
    status_data.set('parameters.test.data_created.principal_counter', principal_counter)
    status_data.set('parameters.test.data_created.errors_counter', errors_counter)

    return rbac_test_data


def main():
    parser = argparse.ArgumentParser(
        description='Create bunch of RBAC tenants and populate them',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('--application', type=list, default=["approval", "advisor"],
                        help='application permissions to be considered')

    parser.add_argument('--tenants-number', type=int, default=1,
                        help='Number of tenants to create')
    
    parser.add_argument('--groups-number', type=int, default=0,
                        help='Number of groups per tenants to create')
    
    parser.add_argument('--roles-number', type=int, default=0,
                        help='Number of roles per group to create')
    
    parser.add_argument('--principals-number', type=int, default=0,
                        help='Number of principals per tenant to create. Will be member of all created groups')
    
    parser.add_argument('--test-data-file', default='/tmp/rbac-test-data.json',
                        help='File where to add test data created here')
    
    parser.add_argument('--rbac-url-suffix',
                        default=os.getenv('RBAC_URL_SUFFIX', '/api/rbac/v1'),
                        help='Test host URL suffix (also use env variable TEST_URL_SUFFIX)')
    
    parser.add_argument('--rbac-host', dest='rbac_host',
                        default=os.getenv('LOCUST_HOST', 'http://rbac.qa.svc:8080'),
                        help='Locust host to test (also use env variable LOCUST_HOST)')
    opl.args.add_rbac_db_opts(parser)
    with opl.skelet.test_setup(parser) as (args, status_data):
        rbac_test_data = opl.rbac_utils.RbacTestData(args.test_data_file)
        return doit(rbac_test_data, args, status_data)


if __name__ == "__main__":
    sys.exit(main())
