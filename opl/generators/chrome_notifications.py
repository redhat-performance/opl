# Generator of payloads for notifications.drawer messages to the platform.chrome topic.
# sample message:
# echo '{"specversion":"1.0.2","type":"notifications.drawer","source":"https://whatever.service.com","id":"test-message","time":"2023-05-23T11:54:03.879689005+02:00","datacontenttype":"application/json","data":{"broadcast":true,"payload":{"id":"foo.bar.1","description":"string","title":"string","created":"2023-05-23T11:54:03.879689005+02:00","read":false,"source":"string"}}}'

import json
import os.path
import random

import opl.gen
import opl.generators.packages
import opl.generators.generic


class ChromeNotificationsGenerator(opl.generators.generic.GenericGenerator):
    def __init__(
        self,
        count=100,
        template="chrome_notifications_template.json.j2",
    ):
        super().__init__(count=count, template=template, dump_message=False)

        # Load package profile generator
        self.pg = opl.generators.packages.PackagesGenerator(self.package_file)

    # def _mid(self, data):
    #     return data["inventory_id"]

    def _data(self):
        return {
            "id": self.gen_uuid(),
            "payload_id": self.gen_uuid(),
            "time": self.gen_datetime(),
            "title": self.gen_string(),
        }
