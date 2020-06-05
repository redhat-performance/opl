import json
import os.path
import random
import jinja2
import jinja2.meta

import opl.gen


class EgressHostsGenerator:
    def __init__(self, expected=1):
        assert expected >= 1   # how many hosts to generate
        self.expected = expected
        self.generated = 0   # how many we have already generated

        # Load data file
        data_dirname = os.path.dirname(__file__)
        data_file = os.path.join(data_dirname, 'inventory_egress_data.json')
        with open(data_file, 'r') as fp:
            self.data = json.load(fp)

        # Load Jinja2 stuff
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(data_dirname))
        template_name = 'inventory_egress_template.json.j2'
        self.template = self.env.get_template(template_name)

    def __iter__(self):
        return self

    def __next__(self):
        if self.generated >= self.expected:
            raise StopIteration

        inventory_id = opl.gen.gen_uuid()
        account = opl.gen.gen_account()
        variables = {
            'INVENTORY_ID': inventory_id,
            'INSIGHTS_ID': opl.gen.gen_uuid(),
            'ACCOUNT_ID': account,
            'FQDN': opl.gen.gen_hostname(),
            'INSTALLED_PACKAGES': random.sample(
                [random.choice(pkg_list) for
                    pkg_list in self.data['PACKAGES'].values()],
                300),
            'YUM_REPOS': self.data['ENABLED_REPOS']
                + random.sample(self.data['AVAILABLE_REPOS'], 10),   # noqa: W503
            'B64_IDENTITY': opl.gen.get_auth_header(account, 'tester')
        }

        self.generated += 1

        return (inventory_id, self.template.render(**variables))
