import json
import os.path
import random
import jinja2
import jinja2.meta

import opl.gen
import opl.generators.packages
import opl.generators.generic


class EgressHostsGenerator(opl.generators.generic.GenericGenerator):
    def __init__(self, count=1, n_packages=300, template='inventory_egress_template.json.j2' , msg_type='created', per_account_data=[]):
        super().__init__(count=count, template=template , dump_message=False)

        self.n_packages = n_packages   # how many packages to put into profile
        self.msg_type = msg_type
        self.per_account_data = per_account_data

        # Load package profile generator
        self.pg = opl.generators.packages.PackagesGenerator()

        # Load data file
        data_dirname = os.path.dirname(__file__)
        data_file = os.path.join(data_dirname, 'inventory_egress_data.json')
        with open(data_file, 'r') as fp:
            self.data = json.load(fp)

        # Check parameters sanity
        assert self.pg.count() >= self.n_packages, \
            "Number of requested packages needs to be lower than available packages"

    def _mid(self, data):
        return data['inventory_id']

    def _data(self):
        if self.per_account_data == []:
            account = self._get_account()
            os_tree_commit = "ec3c003da4eafaa971b528b3383d8caff688a110e53af71a85e666cf60b4ed20"
        else:
            account = random.choice([i['account'] for i in self.per_account_data])
            os_tree_commit = random.choice([i['os_tree_commits'] for i in self.per_account_data if i['account'] == account][0])
        return {
            'inventory_id': self._get_uuid(),
            'insights_id': self._get_uuid(),
            'account': account,
            'os_tree_commit': os_tree_commit,
            'fqdn': self._get_hostname(),
            'installed_packages': self.pg.generate(self.n_packages),
            'yum_repos': self.data['ENABLED_REPOS']
                + random.sample(self.data['AVAILABLE_REPOS'], 10),   # noqa: W503
            'b64_identity': self._get_b64_identity(account),
            'msg_type': self.msg_type,
            'machine_id': self._get_rhel_machine_id(),
            'subscription_manager_id': self._get_uuid(),
            'bios_uuid': self._get_bios_uuid(),
            'ipv4_addr': self._get_ipv4(),
            'ipv6_addr': self._get_ipv6(),
            'mac_addr': self._get_mac(),
            'request_id': self._get_uuid(),
            'nowz': self._get_now_iso_z(),
            'tommorowz': self._get_tommorow_iso_z(),
        }


