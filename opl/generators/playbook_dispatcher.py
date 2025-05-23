import uuid
import opl.generators.generic


class RunnerUpdatesGenerator(opl.generators.generic.GenericGenerator):
    """Iterator that creates payloads with messages formatted using given template."""

    def __init__(
        self,
        count,
        org_id,
        correlation_id,
        run_id,
        template="playbook-dispatcher-runner-updates.json.j2",
    ):
        super().__init__(count=count, template=template, dump_message=False)

        self.counter = 0  # how many payloads we have produced already

        self.correlation_id = correlation_id
        self.run_id = run_id
        self.org_id = org_id

    def _mid(self, data):
        return data["correlation_id"]

    def _headers(self, data):
        return {
            "x-rh-insights-request-id": uuid.uuid4().hex,
            "x-rh-insights-playbook-dispatcher-correlation-id": data["correlation_id"],
            "service": "playbook",
        }

    def _data(self):
        data = {
            "correlation_id": self.correlation_id,
            "run_id": self.run_id,
            "org_id": self.org_id,
            "b64_identity": self._get_b64_identity(self.org_id, self.org_id),
        }
        return data


class RunsPostGenerator(opl.generators.generic.GenericGenerator):
    """Iterator that creates payloads with messages formatted using given template."""

    def __init__(
        self,
        count,
        template="playbook-dispatcher-post-run.json.j2",
    ):
        super().__init__(count=count, template=template, dump_message=False)

        self.counter = 0  # how many payloads we have produced already

    def _mid(self, data):
        return None

    def _data(self):
        data = {
            "recipient": self._get_uuid(),
            "org_id": self._get_orgid(),
        }
        return data
