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


class InventoryIngressGenerator:
    """Iterator that creates payloads with messages formatted using given template."""

    installed_packages = []

    def __init__(self, count, fraction=1, relatives=100, addresses=3, packages=500, template='inventory_ingress_RHSM_template.json.j2'):   # noqa: E501
        self.count = count   # how many payloads to produce
        self.counter = 0   # how many payloads we have produced already
        self.sent = []   # track IDs of profiles we have sent already
        assert fraction > 0
        self.fraction = fraction   # how often we should be returning new system
        self.relatives = self._get_relatives(relatives)   # list of accounts/... to choose from
        self.addresses = addresses   # how many IP and MAC addresses should the host have
        self.packages = packages   # how many packages should be in RHSM package profile
        self.template = template

        assert fraction == 1, "'fraction' handling not yet implemented, please just use 1"
        assert addresses == 3, "'addresses' handling not yet implemented, please just use 3"

        # This will be used to generate list of packages
        self.packages = packages
        self.pg = opl.generators.packages.PackagesGenerator()

        # Load Jinja2 stuff
        data_dirname = os.path.dirname(__file__)
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(data_dirname))

        logging.info(f"Created PayloadGenerator(count={self.count})")

    def __iter__(self):
        return self

    def _get_relatives(self, count):
        return [{
            'account': self._get_account(),
            'orgid': self._get_orgid(),
            'satellite_id': self._get_uuid(),
            'satellite_instance_id': self._get_uuid(),
        } for i in range(count)]

    def _get_uuid(self):
        return str(uuid.uuid4())

    def _get_rhel_machine_id(self):
        return ''.join(random.choices(string.hexdigits, k=32)).lower()

    def _get_bios_uuid(self):
        return self._get_uuid().upper()

    def _get_hostname(self):
        return ''.join(random.choices(string.ascii_lowercase, k=10)) + '.example.com'

    def _get_metadata(self):
        return {"request_id": self._get_uuid(), "archive_url": "http://s3.aws.com/redhat/insights/1234567"}

    def _get_ipv4(self):
        return f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

    def _get_ipv6(self):
        return f"{random.randrange(16**4):x}:{random.randrange(16**4):x}::{random.randrange(16**4):x}:{random.randrange(16**4):x}:{random.randrange(16**4):x}"

    def _get_mac(self):
        tmp = []
        for i in range(6):
            tmp.append(random.randint(0, 255))
        return ":".join([f"{i:02x}" for i in tmp])

    def _get_now_iso(self):
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()   # noqa: E501

    def _get_now_iso_z(self):
        return self._get_now_iso().replace('+00:00', 'Z')

    def _get_tommorow_iso(self):
        return (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()   # noqa: E501

    def _get_tommorow_iso_z(self):
        return self._get_tommorow_iso().replace('+00:00', 'Z')

    def _get_ips_macs(self, count):
        ips = ['127.0.0.1']
        macs = [self._get_mac()]
        count -= 1
        for i in range(count):
            ips.append(self._get_ip())
            macs.append(self._get_mac())
        return (ips, macs)

    def _get_account(self):
        return f"{random.randrange(10**6):07d}"

    def _get_orgid(self):
        return f"{random.randrange(10**6):d}"

    def _get_template_vars(self, tmpl):
        # https://jinja.palletsprojects.com/en/2.10.x/api/#jinja2.meta.find_undeclared_variables
        ast = self.env.parse(self.env.loader.get_source(self.env, tmpl)[0])
        return jinja2.meta.find_undeclared_variables(ast)

    def _get_b64_identity(self, account):
        data = {
            "identity": {
                "account_number": account,
                "fqdn": "fquhahomjr.example.com",
                "type": "User",
                "user": {
                    "username": "tuser@redhat.com",
                    "email": "tuser@redhat.com",
                    "first_name":"test",
                    "last_name":"user",
                    "is_active":"true",
                    "is_org_admin": "false",
                    "is_internal":"true",
                    "locale":"en_US"
                }
            }
        }
        return base64.b64encode(bytes(json.dumps(data).encode('UTF-8'))).decode()

    def _get_disk_devices(self):
        device = ["/dev/fdd2", "/dev/fdd0", "/dev/fdd1"]
        label = ["bar", "foo", "baz"]
        mount_point = ["/mnt/local_nfs", "/mnt/foo", "/mnt/remote_nfs_shares"]
        type = ["ext1", "ext2", "ext3"]
        return {
            "device": random.choice(device),
            "label": random.choice(label),
            "mount_point": random.choice(mount_point),
            "type": random.choice(type)
        }

    def _get_rpm_ostree_deployment(self):
        id = ["fedora-blackpink-63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb.0",
              "fedora-silverblue-63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb.0",
              "fedora-orangeblue-63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb.0"]
        checksum = ["83335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb", 
                    "63335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb",
                     "73335a77f9853618ba1a5f139c5805e82176a2a040ef5e34d7402e12263af5bb"]
        origin = ["fedora/31/x86_64/blackpink", "fedora/34/x86_64/orangeblue", "fedora/33/x86_64/silverblue"]
        osname = ["fedora-blackpink", "fedora-silveblue", "fedora-orangeblue"]
        version = ["33.45", "31.12", "33.21"]
        return {
            "id": random.choice(id),
            "checksum": random.choice(checksum),
            "origin": random.choice(origin),
            "osname": random.choice(osname),
            "version": random.choice(version),
            "booted": False,
            "pinned": False
        }

    def _get_system_purpose(self):
        purposes = [{"usage": "Production", "role": "Red Hat Enterprise Linux Server", "sla": "Premium"},\
                    {"usage": "Development/Test", "role": "Red Hat Enterprise Linux Workstation", "sla": "Standard"}, \
                    {"usage": "Disaster Recovery", "role": "Red Hat Enterprise Linux Compute Node", "sla": "Self-Support"}]
        return random.choice(purposes)

    def _get_ansible(self):
        ansible_profiles = [{
                "controller_version": "1.2.3",
                "hub_version": "1.2.3",
                "catalog_worker_version": "1.2.3",
                "sso_version": "1.2.3"
            }, {
                "controller_version": "4.5.6",
                "hub_version": "4.5.6",
                "catalog_worker_version": "4.5.6",
                "sso_version": "4.5.6"
            }, {
                "controller_version": "7.8.9",
                "hub_version": "7.8.9",
                "catalog_worker_version": "7.8.9",
                "sso_version": "7.8.9"
            }]
        return random.choice(ansible_profiles)

    def _get_operating_system(self):
        operating_systems = [{
                "major": 0,
                "minor": 0,
                "name": "RHEL"
            }, {
                "major": 1,
                "minor": 1,
                "name": "FED"
            }, {
                "major": 2,
                "minor": 2,
                "name": "RHEL"
            }
        ]
        return random.choice(operating_systems)

    def _get_rhsm(self):
        rhsm_profiles = [{
                "version": "8.1"
            }, {
                "version": "7.5"
            }, {
                "version": "9.9"
            }
        ]
        return random.choice(rhsm_profiles)

    def _get(self):
        """
        Generate message and its ID
        """
        template = self.env.get_template(self.template)
        data = {
            'subscription_manager_id': self._get_uuid(),
            'bios_uuid': self._get_bios_uuid(),
            'request_id': self._get_uuid(),
            'owner_id': self._get_uuid(),
            'cpu_model': random.choice(["Intel(R) Xeon(R) CPU E5-2690 0 @ 2.90GHz", "Intel(R) Xeon(R) CPU E9-7800 0 @ 1.90GHz", "Intel(R) I7(R) CPU I7-10900k 0 @ 4.90GHz"]),
            'operating_system': json.dumps(self._get_operating_system()),
            'installed_packages': random.choice(["krb5-libs-0:-1.16.1-23.fc29.i686", "arb5-libs-0:-1.16.1-23.fc29.i686", "brb5-libs-0:-1.16.1-23.fc29.i686"]),
            'tuned_profile': random.choice(["desktop", "example", "laptop"]),
            'selinux_current_mode': random.choice(['sleeping', 'enforcing', 'not_enforcing']),
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
        msg = json.loads(template.render(**data))
        mid = data['subscription_manager_id']
        return mid, msg

    def __next__(self):
        if self.counter == self.count:
            raise StopIteration()

        mid, msg = self._get()
        self.counter += 1
        return mid, msg


class PayloadRHSMGenerator(InventoryIngressGenerator):
    """This is just a nickname so we do not need to change existing code."""

    pass
