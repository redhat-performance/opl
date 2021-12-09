import argparse
import collections
import logging
import os

import opl.investigator.check
import opl.investigator.config
import opl.investigator.csv_loader
import opl.investigator.elasticsearch_decisions
import opl.investigator.elasticsearch_loader
import opl.investigator.status_data_loader

import tabulate


STATUSES = {
    0: 'PASS',
    1: 'FAIL',
    2: 'ERROR',
}


def main():
    parser = argparse.ArgumentParser(
        description='Given historical numerical data, determine if latest result is PASS or FAIL',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--config', type=argparse.FileType('r'), required=True,
                        help='Config file to use')
    parser.add_argument('--current-file', type=argparse.FileType('r'),
                        help='Status data file with results to investigate. Overwrites current.file value from config file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Investigate result, but do not upload decisions. Meant for debugging')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug output')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    opl.investigator.config.load_config(args, args.config)

    if args.current_type == 'status_data':
        current_sd = opl.investigator.status_data_loader.load(args.current_file)
    else:
        raise Exception("Not supported data source type for current data")

    args.sets = opl.investigator.config.render_sets(args.sets, {'current': current_sd, 'environ': os.environ})

    current = opl.investigator.status_data_loader.load_data(current_sd, args.sets)
    total = len([v for v in current.values() if v is not None and v is not ''])
    if total == 0:
        raise Exception(f"No data available in current result!")

    if args.history_type == 'csv':
        history = opl.investigator.csv_loader.load(args.history_file, args.sets)
    if args.history_type == 'elasticsearch':
        args.history_es_query = opl.investigator.elasticsearch_loader.render_query(args.history_es_query, {'current': current_sd, 'environ': os.environ})
        history = opl.investigator.elasticsearch_loader.load(args.history_es_server, args.history_es_index, args.history_es_query, args.sets)
    else:
        raise Exception("Not supported data source type for historical data")

    total = sum([len(v) for v in history.values()])
    if total == 0:
        raise Exception(f"No data available in historical results!")

    exit_code = 0
    summary = []
    info_all = []
    for var in args.sets:
        try:
            results, info = opl.investigator.check.check(history[var], current[var], description=var)
        except Exception as e:
            logging.warning(f"Check on {var} failed with: {e}")
            info_all.append({"result": "ERROR", "exception": str(e)})
            summary_this = collections.OrderedDict([("data set", var), ("exception", str(e))])
            exit_code = 2
        else:
            info_all += info
            result_overall = False not in results
            summary_this = collections.OrderedDict()
            summary_this["data set"] = var
            summary_this.update({i['method']: i['result'] for i in info})
            if exit_code == 0 and not result_overall:
                exit_code = 1

        summary.append(summary_this)

    print("\n", tabulate.tabulate(info_all, headers="keys", tablefmt="simple", floatfmt=".3f"))
    print("\n", tabulate.tabulate(summary, headers="keys", tablefmt="simple"))
    print(f"\nOverall status: {STATUSES[exit_code]}")

    if not args.dry_run and args.decisions_type == 'elasticsearch':
        opl.investigator.elasticsearch_decisions.store(args.decisions_es_server, args.decisions_es_index, info_all)

    return exit_code
