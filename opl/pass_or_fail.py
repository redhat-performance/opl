import argparse
import collections
import logging

import opl.investigator.check
import opl.investigator.config
import opl.investigator.csv_loader
import opl.investigator.elasticsearch_decisions
import opl.investigator.elasticsearch_loader
import opl.investigator.status_data_loader

import tabulate


def main():
    parser = argparse.ArgumentParser(
        description='Given historical numerical data, determine if latest result is PASS or FAIL',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--config', type=argparse.FileType('r'), required=True,
                        help='Config file to use')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug output')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    opl.investigator.config.load_config(args, args.config)

    if args.current_type == 'status_data':
        current, current_sd = opl.investigator.status_data_loader.load(args.current_file, args.sets)
    else:
        raise Exception("Not supported data source type for current data")

    if args.history_type == 'csv':
        history = opl.investigator.csv_loader.load(args.history_file, args.sets)
    if args.history_type == 'elasticsearch':
        args.history_es_query = opl.investigator.elasticsearch_loader.render_query(args.history_es_query, {'current': current_sd})
        history = opl.investigator.elasticsearch_loader.load(args.history_es_server, args.history_es_index, args.history_es_query, args.sets)
    else:
        raise Exception("Not supported data source type for historical data")

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

    if args.decisions_type == 'elasticsearch':
        opl.investigator.elasticsearch_decisions.store(args.decisions_es_server, args.decisions_es_index, info_all)

    return exit_code
