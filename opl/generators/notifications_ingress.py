import json
import os.path
import random
import jinja2
import jinja2.meta

import opl.gen
import opl.generators.packages
import opl.generators.generic
import generic


class EgressHostsGenerator(generic.GenericGenerator):
    def __init__(
        self,
        count=1,
        template="notifications_ingres_template.json.j2",
    ):
        # per_account_data=[] is a json stored in /tmp/edge-test-data.json
        # the value it takes is in the form :
        # [{"account": "5735447", "image_set_id": [529, 530, 531, 532, 533], "repo_ids": [521, 522, 523, 524, 525], "commit_ids": [518, 519, 520, 521, 522], "installer_ids": [517, 518, 519, 520, 521], "image_ids": [513, 514, 515, 516, 517], "os_tree_commits": ["xvsff05dvuj7aocz9qlkrb6uejydysk1eqwjf9xxx1w82l2sh0i7ig6ugqm8l48m", "2rs005sauq3ntnej1bjsjtifxvheutmsq2qx33yur82vcqbb9rj9xjg2c3oyswno", "mu6o43nao29kher8ifscq7zfs3vl2xhcnym577ombmgu5ds11nbdnvwhaudrwz6v", "6c5bnbjupgezd3chkje68gor52jy6j1rmz8ly1vnve4ovvwdopiek4v73z4wqrwc", "eh14yfr96myfmm6md32gcsw0zzvqey22dk4i0uersyygfmp32svi83n8ast0jv0s"]}, {"account": "9631291", "image_set_id": [534, 535, 536, 537, 538], "repo_ids": [526, 527, 528, 529, 530], "commit_ids": [523, 524, 525, 526, 527], "installer_ids": [522, 523, 524, 525, 526], "image_ids": [518, 519, 520, 521, 522], "os_tree_commits": ["wpnzoein8phupqnp7yrnq5cz3nil85ehsnykxloiu7h1iwnw6lztps728rusyzcq", "ha0eg0jl3a0caqrd9nor7ctmp4a4z1zv330lp966kz644dq8nq5gaoj3sx9ofuig", "61t92g7j5gzxxerf163qvp46t9t28j58eth3iu7fkh8xwd3rjqc9j7ff0qxhp4be", "0k1kop8p7ezbmygv7p7yj3nhzrz28g53v9wokbqd3f7pbhpcmllwxrw186fp42v8", "zz1ex8mkwmromvl5b3oxuxvjqpxgesyga9dujelz3rh4sucitoloypbi0psh2d5h"]}]

        super().__init__(count=count, template=template, dump_message=False)

    def _data(self):

        return {
            "notifications_id": self._get_uuid(),
            "account": "12345",
            "fqdn": self._get_hostname(),
            "request_id": self._get_uuid(),
            "nowz": self._get_now_iso_z(),
            "msg_type": "created",
            "subscription_manager_id": self._get_uuid()
        }