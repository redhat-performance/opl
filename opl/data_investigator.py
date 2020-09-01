import logging
import os
import argparse
import requests
import tempfile
import json

import collections
import statistics
import scipy.stats

from . import status_data


class DataInvestigator():

    def __init__(self):
        """
        'data' is a dict of N metrics with names:

        data = {
            'data row name': [1, 3, 4, 2, 2, 1, 4],
            'another data row name': [0.8, 0.9, 0.5, 0.6, 0.8, 0.9, 0.7],
            ...
        }
        """
        self.data = {}
        self._usable = None

    def add(self, name, values):
        if name in self.data:
            raise KeyError(f'Key {name} already exists in data')
        self.data[name] = values
        self._usable = None

    def append(self, name, value):
        if name not in self.data:
            self.data[name] = []
        self.data[name].append(value)
        self._usable = None

    @property
    def usable(self):
        if self._usable is None:
            self.determine_usable()
        return self._usable

    @staticmethod
    def is_usable(data):
        try:
            trim_mean = float(scipy.stats.trim_mean(data, 0.1))
        except TypeError:
            logging.debug(f"Data are giving TypeError - maybe it is list of datetime strings? Ignoring")
            return False
        pstdev = statistics.pstdev(data)
        if 2 * pstdev > trim_mean:
            logging.debug(f"Data failed '2 * pstdev > trim_mean' criteria => not usable")
            return False

        trim_min = min(scipy.stats.trimboth(data, 0.1))
        trim_max = max(scipy.stats.trimboth(data, 0.1))
        if trim_min > 0 and trim_max - trim_min > trim_min:
            logging.debug(f"Data failed 'trim_min > 0 and trim_max - trim_min > trim_min' criteria => not usable")
            return False

        return True

    def determine_usable(self):
        self._usable = {}
        for k, v in self.data.items():
            if self.is_usable(v):
                logging.debug(f"Data set f{k} considered usable")
                self._usable[k] = v

    def check_test_data(self, test_data):
        if self.data.keys() == test_data.keys():
            return True
        else:
            logging.warning(f"Some keys are missing in the test data:\n    data: {self.data.keys()}\n    test: {str(test_data.keys())[:100]}")
            return False

    def test_data(self, test_data):
        fails = []
        for key in set(self.usable.keys()).intersection(test_data.keys()):
            trim_mean = scipy.stats.trim_mean(self.usable[key], 0.1)
            pstdev = statistics.pstdev(self.usable[key])
            tolerance = max([pstdev, trim_mean * 0.25])
            if tolerance == 0:
                tolerance = 1
            lower_boundary = trim_mean - 2 * tolerance
            upper_boundary = trim_mean + 2 * tolerance
            logging.debug(f"Processing {key} which have trim_mean={trim_mean} and pstdev={pstdev}, i.e. tolerance={tolerance} and boundaries={lower_boundary}--{upper_boundary}")
            if not (lower_boundary <= test_data[key] <= upper_boundary):
                logging.warning(f"Result for {key}: FAIL   {lower_boundary:.03f} < {test_data[key]:.03f} < {upper_boundary:.03f}")
                fails.append(key)
        return fails

    def _printabe_data(self, data):
        if isinstance(data[0], str):
            return f"{' '.join(data)}   ({len(data)} samples)"
        else:
            return f"{' '.join([f'{i:.02f}' for i in data])}   ({len(data)} samples)"

    def show(self):
        out = []
        for name, data in self.data.items():
            out.append(f"Processing {name}:")
            out.append(get_info_value('data', self._printabe_data(data)))
        return "\n".join(out)

    def analysis(self):
        out = []
        for name, data in self.data.items():
            out.append(f"Processing {name}:")
            out.append(get_info_value('data', self._printabe_data(data)))

            is_usable = self.is_usable(data)
            out.append(get_info_value('Is usable', is_usable))

            try:
                mean = statistics.mean(data)
            except TypeError:
                out.append(get_info_value('Does not compute', True))
                return "\n".join(out)
            stdev = statistics.stdev(data)
            out.append(get_info_bar('mean vs stdev', ['mean', 'stdev'], [mean, stdev]))

            try:
                trim_mean = scipy.stats.trim_mean(data, 0.1)
            except TypeError:
                out.append(get_info_value('Does not compute', True))
                return "\n".join(out)
            pstdev = statistics.pstdev(data)
            out.append(get_info_bar('trim_mean vs pstdev', ['trim_mean', 'pstdev'], [trim_mean, pstdev]))

            trim_min = min(scipy.stats.trimboth(data, 0.1))
            trim_max = max(scipy.stats.trimboth(data, 0.1))
            out.append(get_info_bar('trim min vs max', ['trim_min', 'trim_max'], [trim_min, trim_max]))

            measure = []
            for i in range(len(data) - 1):
                measure.append(data[i + 1] >= data[i])
            c = collections.Counter(zip(measure, measure[1:]))
            c1 = c[(True, True)] + c[(False, False)]
            c2 = c[(True, False)] + c[(False, True)]
            out.append(get_info_bar('up-down direction', ['same', 'mix'], [c1, c2]))

            measure = []
            mean = statistics.mean(data)
            for i in data:
                measure.append(i >= mean)
            c = collections.Counter(zip(measure, measure[1:]))
            c1 = c[(True, True)] + c[(False, False)]
            c2 = c[(True, False)] + c[(False, True)]
            out.append(get_info_bar('above-below mean', ['same', 'mix'], [c1, c2]))

            measure = []
            mean = scipy.stats.trim_mean(data, 0.1)
            for i in data:
                measure.append(i >= mean)
            c = collections.Counter(zip(measure, measure[1:]))
            c1 = c[(True, True)] + c[(False, False)]
            c2 = c[(True, False)] + c[(False, True)]
            out.append(get_info_bar('above-below trimmed mean', ['same', 'mix'], [c1, c2]))

            entropy = scipy.stats.entropy(list(collections.Counter(data).keys()), base=2)
            out.append(get_info_value('entropy', entropy))

            return "\n".join(out)


def align_label(text, width):
    if len(text) > width:
        text = text[:width - 1] + "…"
    text = text.rjust(width)
    return text


def get_info_value(main_label, value):
    main_label_width = 30

    main_label = align_label(main_label, main_label_width)

    if isinstance(value, float):
        value_str = f"{value:.05f}"
    else:
        value_str = f"{value}"

    return f"{main_label}: {value_str}"


def get_info_bar(main_label, labels, values):
    main_label_width = 30
    labels_total_width = 30
    label_max_width = 10
    values_total_width = 60

    main_label = align_label(main_label, main_label_width)
    aligned_labels = []
    labels_width = min([label_max_width, int(round(labels_total_width / len(labels)))])
    for i in labels:
        aligned_labels.append(align_label(i, labels_width))

    out = ''
    out += f"{main_label}: "

    values_width = int(round(values_total_width / len(values)))
    one_char_value = sum(values) / values_width
    if one_char_value == 0:
        one_char_value = 1
    drawn_so_far = 0
    for label, value in zip(aligned_labels, values):
        value_on_width = int(round(value / one_char_value))
        value_off_width = values_width - drawn_so_far - value_on_width
        out += f"{label} ({value:9.02f}): [{'_' * drawn_so_far}{'#' * value_on_width}{'_' * value_off_width}]"
        drawn_so_far += value_on_width

    if len(values) == 2:
        label = align_label('ratio', labels_width)
        try:
            ratio = float(values[0]) / float(values[1])
            ratio_str = f"{ratio:.02f}"
        except ZeroDivisionError:
            ratio_str = 'nan'
        out += f"{label}: {ratio_str}"

    return out


def doit_append_cli_options_data(data, data_investogator):
    data_row = 0
    for d in data:
        data_name = f"Data_{data_row:03d}"
        data_points = [float(i) for i in d.split(',')]
        data_investogator.add(data_name, data_points)
        data_row += 1


def doit_append_status_files_data(files, data_investogator):
    for f in files:
        sd = status_data.StatusData(f.name)
        for key in sd.list('results') + sd.list('measurements'):
            data_investogator.append(key, sd.get(key))


def doit_append_es_data(data_from_es,
                        data_from_es_matcher,
                        data_from_es_wildcard,
                        es_host,
                        es_port,
                        es_index,
                        es_type,
                        data_investogator):
    if not data_from_es:
        return
    url = f"http://{es_host}:{es_port}/{es_index}/{es_type}/_search"
    headers = {
        'Content-Type': 'application/json',
    }
    data_from_es_matcher = dict([(i.split('=')[0], i[len(i.split('=')[0]) + 1:]) for i in data_from_es_matcher])
    data_from_es_wildcard = dict([(i.split('=')[0], i[len(i.split('=')[0]) + 1:]) for i in data_from_es_wildcard])
    filter_match = [{'term': {k + ".keyword": v}} for k, v in data_from_es_matcher.items()]
    filter_wildcard = [{'wildcard': {k: {'value': v}}} for k, v in data_from_es_wildcard.items()]
    data = {
        'query': {
            'bool': {
                'filter': filter_match + filter_wildcard,
            },
        },
        'sort': [
            {
                'started': {'order': 'desc'}
            },
        ],
        'size': 30,
    }
    logging.info(f"Querying ES with url={url}, headers={headers} and json={json.dumps(data)}")
    response = requests.get(url, headers=headers, json=data)
    response.raise_for_status()
    logging.debug(f"Got back this: {response.json()}")
    for item in response.json()['hits']['hits'][::-1]:
        tmpfile = tempfile.NamedTemporaryFile(prefix=item['_id'], delete=False).name
        sd = status_data.StatusData(tmpfile, data=item['_source'])
        for key in sd.list('results') + sd.list('measurements'):
            data_investogator.append(key, sd.get(key))


def doit_load_cli_option_test(data, test_data):
    data_row = 0
    for d in data:
        data_name = f"Data_{data_row:03d}"
        data_points = float(d)
        test_data[data_name] = data_points
        data_row += 1


def doit_load_status_data_test(data, test_data):
    if data:
        sd = status_data.StatusData(data.name)
        for key in sd.list('results') + sd.list('measurements'):
            test_data[key] = sd.get(key)


def main():
    parser = argparse.ArgumentParser(
        description='This and that with the data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--data-from-cli', nargs='+', default=[],
                        help='Coma separated list(s) of numbers to work with')
    parser.add_argument('--test-from-cli', nargs='+', default=[],
                        help='Number(s) to test')
    parser.add_argument('--data-from-status', nargs='+', default=[], type=argparse.FileType('r'),
                        help='List of status data files to load data from')
    parser.add_argument('--test-from-status', type=argparse.FileType('r'),
                        help='Status data file to load and test')
    parser.add_argument('--data-from-es', action='store_true',
                        help='Get status data from ElasticSearch configured by "--es-*" options')
    parser.add_argument('--data-from-es-matcher', nargs='+', default=[],
                        help='Filter only for data with these key/values. Example: "parameters.cluster.pods.insights-inventory-mq-service.count=10"')
    parser.add_argument('--data-from-es-wildcard', nargs='+', default=[],
                        help='Filter only for data with these key/values via wildcard. Example: "parameters.version=*6.6*"')
    parser.add_argument('--es-host', default=os.getenv('ES_HOST', 'elasticsearch.perf.lab.eng.bos.redhat.com'),
                        help='ElasticSearch host')
    parser.add_argument('--es-port', type=int, default=int(os.getenv('ES_PORT', 9286)),
                        help='ElasticSearch port')
    parser.add_argument('--es-index', default=os.getenv('ES_INDEX', 'insights_perf_index'),
                        help='ElasticSearch index')
    parser.add_argument('--es-type', default=os.getenv('ES_TYPE', 'test_type'),
                        help='ElasticSearch type')
    parser.add_argument('--print', action='store_true',
                        help='Print parsed data')
    parser.add_argument('--analyse', action='store_true',
                        help='Analyse numbers we have')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug output')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    data_investogator = DataInvestigator()

    doit_append_cli_options_data(args.data_from_cli, data_investogator)
    doit_append_status_files_data(args.data_from_status, data_investogator)
    doit_append_es_data(args.data_from_es,
                        args.data_from_es_matcher,
                        args.data_from_es_wildcard,
                        args.es_host,
                        args.es_port,
                        args.es_index,
                        args.es_type,
                        data_investogator)

    test_data = {}
    doit_load_cli_option_test(args.test_from_cli, test_data)
    doit_load_status_data_test(args.test_from_status, test_data)

    data_investogator.check_test_data(test_data)

    if args.analyse:
        print(data_investogator.analysis())
    elif args.print:
        print(data_investogator.show())

    fails = data_investogator.test_data(test_data)
    try:
        data_lenght = sum([len(i) for i in data_investogator.data.values()]) / len(data_investogator.data)
    except ZeroDivisionError:
        data_lenght = 0.0

    print(f"Total data sets: {len(data_investogator.data)}")
    print(f"Usable data sets: {len(data_investogator.usable)}")
    print(f"Random data set lenght: {data_lenght:.1f}")
    print(f"Triggered fails: {', '.join(fails)}")
    return len(fails)
