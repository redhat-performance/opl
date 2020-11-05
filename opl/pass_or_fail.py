import argparse
import logging

import opl.investigator.check
import opl.investigator.config
import opl.investigator.csv_loader
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

    if args.history_type == 'csv':
        history = opl.investigator.csv_loader.load(args.history_file, args.sets)
    if args.history_type == 'elasticsearch':
        history = opl.investigator.elasticsearch_loader.load(args.history_es_server, args.history_es_index, args.history_es_query, args.sets)
    else:
        raise Exception("Not supported data source type for historical data")

    if args.current_type == 'status_data':
        current = opl.investigator.status_data_loader.load(args.current_file, args.sets)
    else:
        raise Exception("Not supported data source type for current data")

    exit_code = 0
    for var in args.sets:
        try:
            results, info = opl.investigator.check.check(history[var], current[var], description=var)
        except Exception as e:
            print(f"Checking {var}: ERROR: {e}")
            exit_code = 2
            raise
        else:
            print(tabulate.tabulate(info, headers="keys", tablefmt="psql", floatfmt=".3f"))
            result_overall = False not in results
            results_str = ['P' if i else 'F' for i in results]
            print(f"Checking {var}: {'PASS' if result_overall else 'FAIL'} ({','.join(results_str)})")
            if exit_code == 0 and not result_overall:
                exit_code = 1

    return exit_code
