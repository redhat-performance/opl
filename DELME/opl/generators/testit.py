#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import opl.generators.playbook_dispatcher

generator = opl.generators.playbook_dispatcher.RunnerUpdatesGenerator(
    count=3,
    template='playbook-dispatcher-runner-updates.json.j2',
    correlation_id="123",
    run_id="456",
)

for msg_id, msg_struct in generator:
    print(f"Message {msg_id}: {str(msg_struct)[:100]}")
