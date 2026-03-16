#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pprint

import opl.generators.inventory_egress
import opl.generators.inventory_ingress
import opl.generators.generic

generator = opl.generators.inventory_egress.EgressHostsGenerator(count=1,n_packages=10,)
#generator = opl.generators.generic.GenericGenerator(count=1, template='inventory_egress_template.json.j2')
#generator = opl.generators.generic.GenericGenerator(count=1, template='inventory_ingress_RHSM_template.json.j2')
#generator = opl.generators.inventory_ingress.InventoryIngressGenerator(count=1, fraction=1, relatives=100, addresses=3, packages=10, template='inventory_ingress_RHSM_template.json.j2')

for msg_id, msg_struct in generator:
    print(msg_id)
    pprint.pprint(msg_struct)
