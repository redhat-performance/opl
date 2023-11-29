import argparse
import logging

from . import skelet


class pluginProw:
    def __init__(self, args):
        print("Hello from pluginProw init")
        self.logger = logging.getLogger("opl.showel.pluginProw")

    def list(self):
        print("Hello from pluginProw list")

    def download(self):
        print("Hello from pluginProw download")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--prow-list",
            dest="actions",
            default=[],
            action="append_const",
            const=("prow", "list"),
            help="List runs for specific Prow run",
        )
        group_actions.add_argument(
            "--prow-download",
            dest="actions",
            default=[],
            action="append_const",
            const=("prow", "download"),
            help="Download file from Prow run artifacts",
        )

        group = parser.add_argument_group(
            title="prow",
            description="Options needed to work with Prow",
        )
        group.add_argument(
            "--prow-base-url",
            default="https://gcsweb-ci.apps.ci.l2s4.p1.openshiftapps.com/gcs/origin-ci-test/logs/",
            help="Base URL",
        )
        group.add_argument(
            "--prow-job-name",
            default="periodic-ci-redhat-appstudio-e2e-tests-load-test-ci-daily-10u-10t",
            help="Job name as available in ci-operator/jobs/...",
        )
        group.add_argument(
            "--prow-test-name",
            default="load-test-ci-daily-10u-10t",
            help="Test name as configured in ci-operator/config/...",
        )
        group.add_argument(
            "--prow-artifact-path",
            default="redhat-appstudio-load-test/artifacts/load-tests.json",
            help="Path to the artifact",
        )


class pluginOpenSearch:
    def __init__(self, args):
        print("Hello from pluginOpenSearch init")
        self.logger = logging.getLogger("opl.showel.pluginOpenSearch")

    def upload(self):
        print("Hello from pluginOpenSearch upload")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--opensearch-upload",
            dest="actions",
            default=[],
            action="append_const",
            const=("opensearch", "upload"),
            help="Upload file to OpenSearch if not already there",
        )

        group = parser.add_argument_group(
            title="opensearch",
            description="Options needed to work with OpenSearch",
        )


class pluginHorreum:
    def __init__(self, args):
        print("Hello from pluginHorreum init")
        self.logger = logging.getLogger("opl.showel.pluginHorreum")

    def upload(self):
        print("Hello from pluginHorreum upload")

    def result(self):
        print("Hello from pluginHorreum result")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--horreum-upload",
            dest="actions",
            default=[],
            action="append_const",
            const=("horreum", "upload"),
            help="Upload file to Horreum if not already there",
        )
        group_actions.add_argument(
            "--horreum-result",
            dest="actions",
            default=[],
            action="append_const",
            const=("horreum", "result"),
            help="Get Horreum no-/change signal for a given time range",
        )

        group = parser.add_argument_group(
            title="horreum",
            description="Options needed to work with Horreum",
        )


class pluginResultsDashboard:
    def __init__(self, args):
        print("Hello from pluginResultsDashboard init")
        self.logger = logging.getLogger("opl.showel.pluginResultsDashboard")

    def upload(self):
        print("Hello from pluginResultsDashboard upload")

    @staticmethod
    def args(parser, group_actions):
        group_actions.add_argument(
            "--resultsdashboard-upload",
            dest="actions",
            default=[],
            action="append_const",
            const=("resultsdashboard", "upload"),
            help="Upload file to Results Dashboard if not already there",
        )

        group = parser.add_argument_group(
            title="resultsdashboard",
            description="Options needed to work with Results Dashboard",
        )


PLUGINS = {
    "prow": pluginProw,
    "opensearch": pluginOpenSearch,
    "horreum": pluginHorreum,
    "resultsdashboard": pluginResultsDashboard,
}


def main():
    parser = argparse.ArgumentParser(
        description="Shovel data from A to B",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group_actions = parser.add_argument_group(
        title="actions",
        description="Various high level things you can do",
    )
    for name, plugin in PLUGINS.items():
        plugin.args(parser, group_actions)

    with skelet.test_setup(parser) as (args, status_data):
        logger = logging.getLogger("main")
        for plugin_name, function_name in args.actions:
            logger.info(
                f"Instantiating plugin {plugin_name} for function {function_name}"
            )
            plugin_object = PLUGINS[plugin_name]
            plugin_instance = plugin_object(args)
            getattr(plugin_instance, function_name)()
