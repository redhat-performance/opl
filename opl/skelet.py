import logging
import os
from contextlib import contextmanager

from . import status_data


@contextmanager
def test_setup(parser):
    parser.add_argument('--status-data-file',
                        default=os.getenv('STATUS_DATA_FILE', '/tmp/status-data.json'),
                        help='File where we maintain metadata, results, parameters and measurements for this test run (also use env variable STATUS_DATA_FILE, default to "/tmp/status-data.json")')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug output')
    args = parser.parse_args()

    fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    if args.debug:
        logging.basicConfig(format=fmt, level=logging.DEBUG)
    else:
        logging.basicConfig(format=fmt)

    logging.debug(f"Args: {args}")

    sdata = status_data.StatusData(args.status_data_file)

    try:
        yield (args, sdata)
    finally:
        sdata.save()
