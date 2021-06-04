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
            'insights_id': self._get_uuid(),
            'ipv4_addr': self._get_ipv4(),
            'ipv6_addr': self._get_ipv6(),
            'mac_addr': self._get_mac(),
            'fqdn': self._get_hostname(),
            'nowz': self._get_now_iso_z(),   # well, this is in nano-seconds, but should be in mili-seconds
            'tommorowz': self._get_tommorow_iso_z(),
            'packages': self.pg.generate(self.packages),
        }
        data.update(random.choice(self.relatives))   # add account and orgid
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
