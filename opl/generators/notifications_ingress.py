#!/usr/bin/env python3

import opl.generators.generic


class NotificationsMessagesGenerator(opl.generators.generic.GenericGenerator):
    def __init__(self, count=1, template="notifications_ingres_template.json.j2"):
        super().__init__(count=count, template=template, dump_message=False)

    def _data(self):
        account = self._get_account()

        return {
            "notifications_id": self._get_uuid(),
            "account": account,
            "fqdn": self._get_hostname(),
            "request_id": self._get_uuid(),
            "nowz": self._get_now_iso_z(),
            "msg_type": "created",
            "subscription_manager_id": self._get_uuid(),
        }
