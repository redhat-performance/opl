#!/usr/bin/env python
# -*- coding: UTF-8 -*-

launches_to_check = [
        {
            "name": "InsightsCompliance_runner",
            "history": 10,
            "owner": "jsemjkal",
        },
        {
            "name": "InsightsEdge_runner",
            "history": 10,
            "owner": "rajchauh",
        },
        {
            "name": "InsightsEngine_runner",
            "history": 10,
            "owner": "rajchauh",
        },
        {
            "name": "InsightsFrontEnd_runner",
            "history": 300,
            "owner": "lrios",
        },
        {
            "name": "InsightsInsightsCore_runner",
            "history": 10,
            "owner": "spadakan",
        },
        {
            "name": "InsightsInventory_runner",
            "history": 10,
            "owner": "spadakan",
        },
        {
            "name": "InsightsInventoryHBIPerfTest_runner",
            "history": 10,
            "owner": "spadakan",
        },
        {
            "name": "InsightsNotifications_runner",
            "history": 10,
            "owner": "lrios",
        },
        {
            "name": "InsightsRBAC_runner",
            "history": 10,
            "owner": "rajchauh",
        },
        {
            "name": "InsightsTally_runner",
            "history": 10,
            "owner": "cmusali",
        },
        {
            "name": "InsightsYuptoo_runner",
            "history": 10,
            "owner": "shubansa",
        },
    ]
import yaml
with open("/tmp/ccc.yaml", "w") as fp:
    yaml.dump(launches_to_check, fp)
