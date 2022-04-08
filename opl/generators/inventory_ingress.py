import base64
import logging
import string
import json
import random
import jinja2
import jinja2.meta
import datetime
import uuid
import os

import opl.generators.packages
import opl.generators.packages


class InventoryIngressGenerator(opl.generators.generic.GenericGenerator):
    """Iterator that creates payloads with messages formatted using given template."""

    installed_packages = []

    def __init__(self, count, fraction=1, relatives=100, addresses=3, packages=500, template='inventory_ingress_RHSM_template.json.j2'):   # noqa: E501
        super().__init__(count=count, template=template, dump_message=False)

        self.counter = 0   # how many payloads we have produced already

        assert fraction > 0
        self.fraction = fraction   # how often we should be returning new system
        self.relatives = self._get_relatives(relatives)   # list of accounts/... to choose from
        self.addresses = addresses   # how many IP and MAC addresses should the host have
        self.packages = packages   # how many packages should be in RHSM package profile

        assert fraction == 1, "'fraction' handling not yet implemented, please just use 1"
        assert addresses == 3, "'addresses' handling not yet implemented, please just use 3"

        # This will be used to generate list of packages
        self.packages = packages
        self.pg = opl.generators.packages.PackagesGenerator()

    def _get_relatives(self, count):
        return [{
            'account': self._get_account(),
            'orgid': self._get_orgid(),
            'satellite_id': self._get_uuid(),
            'satellite_instance_id': self._get_uuid(),
        } for i in range(count)]

    def _mid(self, data):
        return data['subscription_manager_id']

    def _data(self):
        data = {
            'subscription_manager_id': self._get_uuid(),
            'bios_uuid': self._get_bios_uuid(),
            'request_id': self._get_uuid(),
            'owner_id': self._get_uuid(),
            'cpu_model': random.choice(["Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz", "Intel(R) Xeon(R) CPU E9-7800 0 @ 1.90GHz", "Intel(R) I7(R) CPU I7-10900k 0 @ 4.90GHz"]),
            'operating_system': json.dumps(self._get_operating_system()),
            'installed_packages': json.dumps([random.choice(["krb5-libs-0:-1.16.1-23.fc29.i686", "arb5-libs-0:-1.16.1-23.fc29.i686", "brb5-libs-0:-1.16.1-23.fc29.i686"])]),
            'tuned_profile': random.choice(["desktop", "example", "laptop"]),
            'selinux_current_mode': random.choice(['enforcing', 'permissive', 'disabled']),
            'selinux_config_file': random.choice(['permissive', 'sleepy', 'authoritative']),
            'rhsm': json.dumps(self._get_rhsm()),
            'rhc_client_id': self._get_uuid(),
            'rhc_config_state': self._get_uuid(),
            'disk_devices': json.dumps([self._get_disk_devices()]),
            'subscription_status': random.choice(["ext1", "ext2", "ext3"]),
            'katello_agent_running': random.choice(['true', 'false']),
            'cloud_provider': random.choice(["aws", "ibm", "ms"]),
            'gpg_pubkeys': json.dumps([random.choice(["gpg-pubkey-22222222-22222222", "gpg-pubkey-22222222-33333333", "gpg-pubkey-11111111-22222222"])]),
            'sap_system': random.choice(["true", "false"]),
            'sap_sids': json.dumps([random.choice(['ABC', 'XYZ', 'H20'])]),
            'sap_instance_number': random.choice(["03", "05", "99"]),
            'sap_version': random.choice(["3.00.122.04.1478575636", "2.00.122.04.1478575636", "1.00.122.04.1478575636"]),
            'is_marketplace': random.choice(['true', 'false']),
            'host_type': random.choice(['edge', 'not_edge']),
            'greenboot_status': random.choice(['red', 'green']),
            'greenboot_fallback_detected': random.choice(['false', 'true']),
            'rpm_ostree_deployments': json.dumps([self._get_rpm_ostree_deployment()]),
            'system_purpose': json.dumps(self._get_system_purpose()),
            'ansible': json.dumps(self._get_ansible()),
            'insights_id': self._get_uuid(),
            'ipv4_addr': self._get_ipv4(),
            'ipv6_addr': self._get_ipv6(),
            'mac_addr': self._get_mac(),
            'fqdn': self._get_hostname(),
            'nowz': self._get_now_iso_z(),   # well, this is in nano-seconds, but should be in mili-seconds
            'tommorowz': self._get_tommorow_iso_z(),
            'packages': self.pg.generate(self.packages),
            'yum_repos': opl.generators.packages.YumReposGenerator().generate(137),
            'enabled_services': opl.generators.packages.EnabledServicesGenerator().generate(139),
            'installed_services': opl.generators.packages.InstalledServicesGenerator() .generate(160),
            'running_processes': opl.generators.packages.RunningProcessesGenerator().generate(89),
        }
        data.update(random.choice(self.relatives))   # add account and orgid
        data.update({'b64_identity': self._get_b64_identity(data['account'])})
        return data


class PayloadRHSMGenerator(InventoryIngressGenerator):
    """This is just a nickname so we do not need to change existing code."""

    pass
