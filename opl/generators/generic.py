#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import string
import json
import random
import jinja2
import jinja2.meta
import datetime
import os

import opl.gen
import opl.date


class GenericGenerator:
    """Iterator that creates payloads with messages formatted using given template."""

    def __init__(self, count, template, dump_message=False):
        assert count >= 1
        self.count = count  # how many messages to generate
        self.template_file = template  # what template file to use
        self.dump_message = dump_message  # stould we generate message as a struct (False, default) or as a byte encoded json string (True)

        self.counter = 0

        # These will be added to variables when rendering template
        # so you can use there e.g. "Random UUID is: {{ opl_gen.gen_uuid() }}"
        self.helpers = {
            "opl_gen": opl.gen,
        }

        data_dirname = os.path.dirname(__file__)
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader(
                [
                    jinja2.FileSystemLoader(data_dirname),
                    jinja2.FileSystemLoader("/home/"),
                ]
            )
        )
        self.template = self.env.get_template(self.template_file)

        logging.info(f"Created {self}")

    def __repr__(self):
        return f"<GenricGenerator({self.count}, {self.template_file}, {self.dump_message})>"

    def __str__(self):
        return str(self.__repr__())

    def __iter__(self):
        return self

    def _get(self):
        """Return tuple with message ID and message content structure"""
        data = self._data()
        mid = self._mid(data)
        if self.dump_message:
            msg = self.template.render(**self.helpers, **data).encode("UTF-8")
        else:
            msg = json.loads(self.template.render(**self.helpers, **data))
        return mid, msg

    def _mid(self, data):
        """Choose what data do we return as a message ID"""
        return data["subscription_manager_id"]

    def _data(self):
        """Prepare data to use in the template"""
        return {
            "subscription_manager_id": self._get_uuid(),
        }

    def __next__(self):
        if self.counter == self.count:
            raise StopIteration()

        mid, msg = self._get()
        self.counter += 1
        return mid, msg

    def dump(self, message):
        """Helper to dump python struct into json string and encode it
        into bytes so it is ready to be produced to Kafka."""
        return json.dumps(message).encode("UTF-8")

    def _get_uuid(self):
        return opl.gen.gen_uuid()

    def _get_rhel_machine_id(self):
        return "".join(random.choices(string.hexdigits, k=32)).lower()

    def _get_bios_uuid(self):
        return opl.gen.gen_uuid().upper()

    def _get_hostname(self):
        return opl.gen.gen_hostname()

    def _get_metadata(self):
        return {
            "request_id": self._get_uuid(),
            "archive_url": "http://s3.aws.com/redhat/insights/1234567",
        }

    def _get_ipv4(self):
        return opl.gen.gen_ipv4()

    def _get_ipv6(self):
        return opl.gen.gen_ipv6()

    def _get_mac(self):
        return opl.gen.gen_mac()

    def _get_now_iso(self):
        return opl.date.get_now_str()  # noqa: E501

    def _get_now_iso_z(self):
        return self._get_now_iso().replace("+00:00", "Z")

    def _get_now_rfc(self):
        rfc_time = opl.date.get_now_str()
        rfc_time = (rfc_time.replace("T", " "))[: len(rfc_time) - 3]
        return rfc_time

    def _get_tommorow_iso(self):
        return (
            opl.date.get_now() + datetime.timedelta(days=1)
        ).isoformat()  # noqa: E501

    def _get_tommorow_iso_z(self):
        return self._get_tommorow_iso().replace("+00:00", "Z")

    def _get_tommorow_rfc(self):
        rfc_time_tommorow = (
            opl.date.get_now() + datetime.timedelta(days=1)
        ).isoformat()
        rfc_time_tommorow = (rfc_time_tommorow.replace("T", " "))[
            : len(rfc_time_tommorow) - 3
        ]
        return rfc_time_tommorow

    def _get_ips_macs(self, count):
        ips = ["127.0.0.1"]
        macs = [self._get_mac()]
        count -= 1
        for i in range(count):
            ips.append(self._get_ipv4())
            macs.append(self._get_mac())
        return (ips, macs)

    def _get_account(self):
        return opl.gen.gen_account()

    def _get_orgid(self):
        return opl.gen.gen_account()

    def _get_template_vars(self, tmpl):
        # https://jinja.palletsprojects.com/en/2.10.x/api/#jinja2.meta.find_undeclared_variables
        ast = self.env.parse(self.env.loader.get_source(self.env, tmpl)[0])
        return jinja2.meta.find_undeclared_variables(ast)

    def _get_b64_identity(self, account, orgid):
        return opl.gen.get_auth_header(
            account=account, user=opl.gen.gen_safe_string(), org_id=orgid
        ).decode()

    def _get_disk_devices(self):
        device = ["/dev/fdd2", "/dev/fdd0", "/dev/fdd1"]
        label = ["bar", "foo", "baz"]
        mount_point = ["/mnt/local_nfs", "/mnt/foo", "/mnt/remote_nfs_shares"]
        type = ["ext1", "ext2", "ext3"]
        return {
            "device": random.choice(device),
            "label": random.choice(label),
            "mount_point": random.choice(mount_point),
            "type": random.choice(type),
        }

    def _get_rpm_ostree_deployment(self):
        id = [
            "fedora-blackpink-63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb.0",
            "fedora-silverblue-63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb.0",
            "fedora-orangeblue-63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb.0",
        ]
        checksum = [
            "83335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb",
            "63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb",
            "73335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb",
        ]
        origin = [
            "fedora/31/x86_64/blackpink",
            "fedora/34/x86_64/orangeblue",
            "fedora/33/x86_64/silverblue",
        ]
        osname = ["fedora-blackpink", "fedora-silveblue", "fedora-orangeblue"]
        version = ["33.45", "31.12", "33.21"]
        return {
            "id": random.choice(id),
            "checksum": random.choice(checksum),
            "origin": random.choice(origin),
            "osname": random.choice(osname),
            "version": random.choice(version),
            "booted": False,
            "pinned": False,
        }

    def _get_system_purpose(self):
        purposes = [
            {
                "usage": "Production",
                "role": "Red Hat Enterprise Linux Server",
                "sla": "Premium",
            },
            {
                "usage": "Development/Test",
                "role": "Red Hat Enterprise Linux Workstation",
                "sla": "Standard",
            },
            {
                "usage": "Disaster Recovery",
                "role": "Red Hat Enterprise Linux Compute Node",
                "sla": "Self-Support",
            },
        ]
        return random.choice(purposes)

    def _get_ansible(self):
        ansible_profiles = [
            {
                "controller_version": "1.2.3",
                "hub_version": "1.2.3",
                "catalog_worker_version": "1.2.3",
                "sso_version": "1.2.3",
            },
            {
                "controller_version": "4.5.6",
                "hub_version": "4.5.6",
                "catalog_worker_version": "4.5.6",
                "sso_version": "4.5.6",
            },
            {
                "controller_version": "7.8.9",
                "hub_version": "7.8.9",
                "catalog_worker_version": "7.8.9",
                "sso_version": "7.8.9",
            },
        ]
        return random.choice(ansible_profiles)

    def _get_operating_system(self, os_override):
        if os_override is not None:
            assert (
                isinstance(os_override, dict),
                'Invalid os_override parameter, should be a dict, maybe something like this: `{"major": 7, "minor": 6, "name": "RHEL"}`, but we have this: '
                + os_override,
            )
            operating_systems = os_override
        else:
            operating_systems = [
                {"major": 7, "minor": 6, "name": "RHEL"},
                {"major": 7, "minor": 7, "name": "RHEL"},
                {"major": 7, "minor": 8, "name": "RHEL"},
                {"major": 7, "minor": 9, "name": "RHEL"},
            ]
        return random.choice(operating_systems)

    def _get_rhsm(self):
        rhsm_profiles = [{"version": "8.1"}, {"version": "7.5"}, {"version": "9.9"}]
        return random.choice(rhsm_profiles)
