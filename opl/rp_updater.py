import argparse
import logging

import opl.http
import opl.status_data

import tabulate


def _get_all_items(args):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.rp_token}",
    }
    url = f"https://{args.rp_host}/api/v1/{args.rp_project}/item"
    params = {
        "filter.eq.launchId": args.rp_launch_id,
        "page.size": 100,
        "page.page": 1,
        # 'page.sort': 'endTime,desc',
    }

    items = []
    while True:
        response = opl.http.get(
            url, params=params, headers=headers, verify=not args.rp_noverify
        )
        items += response["content"]
        if len(response["content"]) == 0:
            logging.debug(f"Page {params['page.page']} was last page of results")
            break
        params["page.page"] += 1
        logging.debug(f"Going to query for page {params['page.page']} of results")

    return items


def doit_list_tests(args):
    items = _get_all_items(args)

    # Add suite name to tests
    suites = {}
    for i in items:
        if i["type"] == "SUITE":
            suites[i["id"]] = i
    for i in items:
        if i["type"] == "TEST":
            i["parent_name"] = suites[i["parent"]]["name"]

    table = [
        (
            i["id"],
            i["type"],
            i["parent_name"] + "/" + i["name"],
            i["status"],
            i["statistics"]["defects"],
        )
        for i in items
        if i["type"] == "TEST"
    ]
    print(tabulate.tabulate(table, headers=("ID", "type", "name", "status", "defects")))


def doit_change_defects(args):
    changes = 0
    items = _get_all_items(args)

    defect_group = args.from_defect.split("/")[0]
    defect_id = args.from_defect.split("/")[1]
    defect_from = {defect_group: {"total": 1, defect_id: 1}}

    defect_to_id = args.to_defect.split("/")[1]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args.rp_token}",
    }
    url = f"https://{args.rp_host}/api/v1/{args.rp_project}/item"

    for i in items:
        if i["type"] != "TEST":
            continue

        if i["statistics"]["defects"] != defect_from:
            continue

        data = {
            "issues": [
                {
                    "testItemId": i["id"],
                    "issue": {
                        "issueType": defect_to_id,
                        "comment": args.to_defect_comment,
                    },
                }
            ]
        }

        opl.http.put(url, headers=headers, data=data, verify=not args.rp_noverify)
        changes += 1

    print(f"Changed {changes} tests from {defect_id} to {defect_to_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Investigate and modify status data documents in ElasticSearch",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--rp-host", help="ReportPortal host")
    parser.add_argument(
        "--rp-noverify",
        action="store_true",
        help="When talking to ReportPortal ignore certificate verification failures",
    )
    parser.add_argument("--rp-project", help="ReportPortal project")
    parser.add_argument("--rp-token", help="ReportPortal token")
    parser.add_argument("--rp-launch-id", help="ReportPortal launch ID")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually change data, meant for debugging",
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug output")

    subparsers = parser.add_subparsers(dest="action", help="Select one of sub-commands")

    # create the parser for the "list_tests" command
    subparsers.add_parser("list_tests", help="Print tests in given launch")

    # create the parser for the "change_defects" command
    parser_change_defects = subparsers.add_parser(
        "change_defects", help="Change defects in given launch"
    )
    parser_change_defects.add_argument(
        "--from-defect", help="Take these defects (e.g. to_investigate/ti001"
    )
    parser_change_defects.add_argument(
        "--to-defect", help="And change them to these defects (e.g. no_issue/ni001)"
    )
    parser_change_defects.add_argument(
        "--to-defect-comment", help="Comment to add to the test with changed defect"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    opl.http.disable_insecure_request_warnings(args.rp_noverify)

    logging.debug(f"Args: {args}")

    if args.action == "list_tests":
        return doit_list_tests(args)
    elif args.action == "change_defects":
        return doit_change_defects(args)
    else:
        raise Exception(f"Unknown action '{args.action}'")
