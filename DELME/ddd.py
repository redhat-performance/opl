#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import sys
import os
import logging
from locust import HttpUser
from locust import constant
from locust import task
import opl.args
import opl.gen
import opl.locust
import opl.skelet
import base64
import json
import size_kb


class TheNotifications(HttpUser):

    wait_time = constant(
        0
    )  # IF performing latency test, then change to 1, but not necessary here

    def getting_headers(self):
        """
        This header was created to avoid issues with WARNING when sending emails
        """
        data = {
            "identity": {
                "associate": {
                    "Role": ["org_admin"],
                    "email": "tester@example.com",
                    "givenName": "tester",
                    "rhatUUID": "01234567-89ab-cdef-0123-456789abcdef",
                    "surname": "tester",
                },
                "auth_type": "saml-auth",
                "type": "Associate",
            }
        }

        return base64.b64encode(json.dumps(data).encode("UTF-8"))

    def _post_availability(self, endpoint, size_payload):
        """Just a helper for a given endpoint with given limit set"""

        url = f"{self.host_base}/{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "x-rh-identity": self.getting_headers(),
        }

        payload = json.dumps(
            {
                "version": "2.0.0",
                "bundle": "rhel",
                "application": "policies",
                "event_type": "policy-triggered",
                "timestamp": "2024-05-29T09:08:31.911475014",
                "account_id": "12345",
                "org_id": "12345",
                "context": {
                    "inventory_id": "93f5896e-91dd-4b9d-a9c4-21ff618ee991",
                    "system_check_in": "2024-05-29T09:08:31.860645",
                    "display_name": "gduval-rhel91",
                    "tags": [
                        {
                            "value": "93f5896e-91dd-4b9d-a9c4-21ff618ee991",
                            "key": "inventory_id",
                        },
                        {"value": "gduval-rhel91", "key": "display_name"},
                    ],
                },
                "events": [
                    {
                        "metadata": {},
                        "payload": size_kb.size_of_dict(size=size_payload),
                    }
                ],
                "recipients": [],
            }
        )

        response = self.client.post(
            url=url, headers=headers, data=payload, verify=False
        )
        return response

    @task(1)
    def check_availability(self):
        """
        first getting sources id and supplying with check_availability
        """

        return self._post_availability("/notifications", self.size_payload)


def doit(args, status_data):

    logging.info(f"Running with test data total counts: {status_data}")
    # Extra args
    test_set = TheNotifications

    test_set.host_base = f"{args.gw_host}"
    args.host = args.gw_host

    test_set.size_payload = int(args.size_payload)

    # Add parameters to status data file.
    status_data.set("name", "Insights NOTIFICATIONS API perf test")
    status_data.set("parameters.locust.hatch_rate", args.hatch_rate)
    status_data.set("parameters.locust.host", args.host)
    status_data.set("parameters.locust.num_clients", args.num_clients)
    status_data.set("parameters.locust.stop_timeout", args.stop_timeout)
    status_data.set("parameters.test.duration", args.test_duration)
    status_data.set("parameters.locust.test-requests", args.test_requests)
    print(
        f"Running with host = {args.gw_host}, num_clients = {args.num_clients}, hatch_rate = {args.hatch_rate} and duration = {args.test_duration} seconds and payload_size(kb) {args.size_payload} and num_requests = {args.test_requests}"
    )

    return opl.locust.run_locust(
        args, status_data, test_set, new_stats=True
    )  # TODO look into tweeking this


def main():

    print("***** Executing Perf testing ******")
    parser = argparse.ArgumentParser(
        description="Measure NOTIFICATIONS API endpoints speed",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--gw_host",
        dest="gw_host",
        default=os.getenv(
            "notifications_gw_host",
            "http://notifications-gw-service.notifications-perf.svc.cluster.local:8000",
        ),  # This is Golang
        help="GW host, use env variable GW_HOST)",
    )

    parser.add_argument(
        "--size_payload",
        dest="size_payload",
        default="40",
        help="Payload size in kb",
    )

    opl.args.add_locust_opts(parser)
    with opl.skelet.test_setup(parser) as (args, status_data):
        logging.info(f"The status data file is {args.status_data_file}")

        return doit(args, status_data)


if __name__ == "__main__":
    sys.exit(main())
