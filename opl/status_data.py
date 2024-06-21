import argparse
import logging
import os
import os.path
import pprint
import deepdiff
import jinja2
import tabulate
from opl import cluster_read, date, skelet
from opl.status import StatusData


def doit_set(status_data, set_this):
    for item in set_this:
        if item == "":
            logging.warning("Got empty key=value pair to set - ignoring it")
            continue

        key, value = item.split("=")

        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]

        if value == "%NOW%":
            value = date.get_now_str()
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass

        logging.debug(f"Setting {key} = {value} ({type(value)})")
        status_data.set(key, value)


def doit_remove(status_data, remove_this):
    for item in remove_this:
        status_data.remove(item)


def doit_set_subtree_json(status_data, set_this):
    for item in set_this:
        if item == "":
            logging.warning("Got empty key=value pair to set - ignoring it")
            continue

        key, value = item.split("=")

        logging.debug(f"Setting {key} = {value} (JSON file)")
        status_data.set_subtree_json(key, value)


def doit_print_oneline(status_data, get_this, get_rounding, get_delimiter):
    if not get_rounding:
        print(get_delimiter.join([str(status_data.get(i)) for i in get_this]))
    else:
        for i in get_this:
            if isinstance(status_data.get(i), float):
                print("{:.2f}".format(status_data.get(i)), end=get_delimiter)
            else:
                print("{}".format(status_data.get(i)), end=get_delimiter)
        print()


def doit_additional(status_data, additional, monitoring_start, monitoring_end, args):
    requested_info = cluster_read.RequestedInfo(
        additional,
        start=monitoring_start,
        end=monitoring_end,
        args=args,
        sd=status_data,
    )

    counter_ok = 0
    counter_bad = 0
    for k, v in requested_info:
        if k is None:
            counter_bad += 1
        else:
            status_data.set(k, v)
            counter_ok += 1

    print(
        f"Gathered {counter_ok} `ok` data points. Not gathered {counter_bad} `bad` data points"
    )


def doit_info(status_data):
    print(status_data.info())


def main():
    parser = argparse.ArgumentParser(
        description="Work with status data file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--set",
        nargs="*",
        default=[],
        help='Set key=value data. If value is "%%NOW%%", current date&time is added',
    )
    parser.add_argument(
        "--set-now", nargs="*", default=[], help="Set key to current date&time"
    )
    parser.add_argument(
        "--set-subtree-json",
        nargs="*",
        default=[],
        help="Set key to structure from json or yaml formated file (detected by *.json or *.yaml file extension)",
    )
    parser.add_argument(
        "--get", nargs="*", default=[], help="Print value for given key(s)"
    )
    parser.add_argument("--remove", nargs="*", default=[], help="Remove given key(s)")
    parser.add_argument(
        "--additional",
        type=argparse.FileType("r"),
        help="Gather more info as specified by the cluster_read.py compatible yaml file",
    )
    parser.add_argument(
        "--monitoring-start",
        type=date.my_fromisoformat,
        help="Start of monitoring interval in ISO 8601 format in UTC with seconds precision",
    )
    parser.add_argument(
        "--monitoring-end",
        type=date.my_fromisoformat,
        help="End of monitoring interval in ISO 8601 format in UTC with seconds precision",
    )
    parser.add_argument(
        "--monitoring-raw-data-dir",
        type=cluster_read.dir_path,
        help="Provide a direcotory if you want raw monitoring data to be dumped in CSV files form",
    )
    parser.add_argument(
        "--end",
        action="store_true",
        help='"started" is set when the status data file is created, "ended" is set when this is used',
    )
    parser.add_argument(
        "--info", action="store_true", help="Show basic info from status data file"
    )
    parser.add_argument(
        "--decimal-rounding",
        action="store_true",
        help="Rounding a number to its hundredths, leaving 2 numbers after decimal point",
    )
    parser.add_argument(
        "--delimiter",
        default="\t",
        help='When returning more "--get" fields, delimit them with this (default is tab)',
    )
    for name, plugin in cluster_read.PLUGINS.items():
        plugin.add_args(parser)

    with skelet.test_setup(parser) as (args, status_data):
        if len(args.set) > 0:
            doit_set(status_data, args.set)
        if len(args.set_now) > 0:
            doit_set(status_data, [k + "=%NOW%" for k in args.set_now])
        if len(args.set_subtree_json) > 0:
            doit_set_subtree_json(status_data, args.set_subtree_json)
        if len(args.get) > 0:
            doit_print_oneline(
                status_data, args.get, args.decimal_rounding, args.delimiter
            )
        if len(args.remove) > 0:
            doit_remove(status_data, args.remove)
        if args.additional:
            doit_additional(
                status_data,
                args.additional,
                args.monitoring_start,
                args.monitoring_end,
                args,
            )
        if args.end:
            doit_set(status_data, ["ended=%NOW%"])
        if args.info:
            doit_info(status_data)


def main_diff():
    parser = argparse.ArgumentParser(
        description="Compare two status data files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("first", nargs=1, help="First file to compare")
    parser.add_argument("second", nargs=1, help="Second file to compare")
    parser.add_argument("--report", action="store_true", help="Show formated report")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    first = StatusData(args.first[0])
    second = StatusData(args.second[0])

    diff = deepdiff.DeepDiff(first._data, second._data, view="tree")
    if args.report:
        print(f"Keys: {', '.join(diff.keys())}")
        if "dictionary_item_added" in diff:
            print("\nDictionary items added:\n")
            table = []
            for i in diff["dictionary_item_added"]:
                table.append([i.path(), i.t2])
            print(tabulate.tabulate(table, headers=["path", "added value"]))
        if "dictionary_item_removed" in diff:
            print("\nDictionary items removed:\n")
            table = []
            for i in diff["dictionary_item_removed"]:
                table.append([i.path(), i.t1])
            print(tabulate.tabulate(table, headers=["path", "removed value"]))
        if "values_changed" in diff:
            print("\nValues changed:\n")
            table = []
            for i in diff["values_changed"]:
                d = None
                try:
                    first = float(i.t1)
                    second = float(i.t2)
                    d_raw = (second - first) / first * 100
                    if abs(d_raw) < 1:
                        d = f"{d_raw:.3f}"
                    else:
                        d = f"{d_raw:.0f}"
                except (ValueError, ZeroDivisionError):
                    pass
                table.append([i.path(), i.t1, i.t2, d])
            print(
                tabulate.tabulate(
                    table, headers=["path", "first", "second", "change [%]"]
                )
            )
        if "type_changes" in diff:
            print("\nTypes changed:\n")
            table = []
            for i in diff["type_changes"]:
                table.append([i.path(), type(i.t1), type(i.t2)])
            print(tabulate.tabulate(table, headers=["path", "first", "second"]))
    else:
        pprint.pprint(diff)


def main_report():
    parser = argparse.ArgumentParser(
        description="Create a report using provided template from status" " data file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("template", help="Report template file to use")
    parser.add_argument("status_data", help="Status data file to format")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    # Load Jinja2 template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(args.template))
    )
    template = env.get_template(os.path.basename(args.template))

    # Load status data document
    data = StatusData(args.status_data)

    print(template.render({"data": data}))
