#!/usr/bin/env python3

import opl.generators.generic


class NotificationsMessagesGenerator(opl.generators.generic.GenericGenerator):
    def __init__(
        self,
        count=1,
        template="notifications_ingres_template.json.j2",
        event_type="integration-failed",
        bundle="console",
        application="integrations",
    ):
        self.event_type = event_type
        self.bundle = bundle
        self.application = application
        super().__init__(count=count, template=template, dump_message=False)

    def _data(self):
        account = self._get_account()

        return {
            "application": self.application,
            "bundle": self.bundle,
            "event_type": self.event_type,
            "notifications_id": self._get_uuid(),
            "account": account,
            "fqdn": self._get_hostname(),
            "request_id": self._get_uuid(),
            "nowz": self._get_now_iso_z(),
            "msg_type": "created",
            "subscription_manager_id": self._get_uuid(),
        }
