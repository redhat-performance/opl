import argparse
import logging
import os
import unicodedata
import junitparser

from . import date


class TestCaseWithProp(junitparser.TestCase):

    def properties(self):
        """
        Iterates through all properties.
        """
        props = self.child(junitparser.Properties)
        if props is None:
            return
        for prop in props:
            yield prop

    def add_property(self, name, value):
        """
        Adds a property to the testsuite.
        """
        props = self.child(junitparser.Properties)
        if props is None:
            props = junitparser.Properties()
            self.append(props)
        prop = junitparser.Property(name, value)
        props.add_property(prop)


class JUnitXmlPlus(junitparser.JUnitXml):

    @classmethod
    def fromfile_or_new(cls, filename):
        if os.path.exists(filename):
            instance = cls.fromfile(filename)
        else:
            instance = cls()
            instance.filepath = filename
        return instance

    def _remove_control_characters(self, s):
        return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C" or ch == "\n")

    def add_to_suite(self, suite_name, new):
        case = TestCaseWithProp(new['name'])

        suite_found = False
        for suite in self:
            if suite.name == suite_name:
                logging.debug(f'Suite {suite_name} found, going to add into it')
                suite_found = True
        if not suite_found:
            logging.debug(f'Suite {suite_name} not found, creating new one')
            suite = junitparser.TestSuite(suite_name)
            self.add_testsuite(suite)

        if new['result'] == 'PASS':
            case.result = []
        elif new['result'] == 'FAIL':
            case.result = [junitparser.Failure(new['message'])]
        elif new['result'] == 'ERROR':
            case.result = [junitparser.Error(new['message'])]
        else:
            raise Exception(f"Invalid result {new['result']}")

        if new['system-out']:
            try:
                case.system_out = self._remove_control_characters(new['system-out'].read())
            except ValueError as e:
                logging.error(f"Failed to load {new['system-out'].name} file: {e}")
        if new['system-err']:
            try:
                case.system_err = self._remove_control_characters(new['system-err'].read())
            except ValueError as e:
                logging.error(f"Failed to load {new['system-err'].name} file: {e}")

        duration = (new['end'] - new['start']).total_seconds()
        case.time = duration

        case.add_property('start', new['start'].isoformat())
        case.add_property('end', new['end'].isoformat())

        suite.add_testcase(case)

        self.write()

    def get_info(self):
        out = []
        for suite in self:
            print(f"suite: {suite}")
            for case in suite:
                case = TestCaseWithProp.fromelem(case)
                print(f"    case: {case}   {case.result}")
                for prop in case.properties():
                    print(f"        property: {prop}")
        return "\n".join(out)

    def delete(self):
        os.remove(self.filepath)


def main():
    parser = argparse.ArgumentParser(
        description='Manipulate jUnit file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--file',
                        default=os.getenv('JUNIT_FILE', 'junit.xml'),
                        help='jUnit file to work with (also use env variable JUNIT_FILE)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug output')
    subparsers = parser.add_subparsers(dest='action',
                                       help='Select one of sub-commands')

    # Create the parser for the "print" command
    parser_print = subparsers.add_parser('print',   # noqa: F841
                                         help='Print content of the file')

    # create the parser for the "add" command
    parser_add = subparsers.add_parser('add',
                                       help='Add testcase into the file')
    parser_add.add_argument('--name', required=True,
                            help='Name of the testcase')
    parser_add.add_argument('--result', required=True,
                            choices=['PASS', 'FAIL', 'ERROR'],
                            help='Result of the testcase')
    parser_add.add_argument('--suite', required=True,
                            help='Testsuite this testcase should be in')
    parser_add.add_argument('--out', type=argparse.FileType('r'),
                            help='File with stdout of the testcase')
    parser_add.add_argument('--err', type=argparse.FileType('r'),
                            help='File with stderr of the testcase')
    parser_add.add_argument('--message',
                            help='Message when result is failure or error')
    parser_add.add_argument('--start', required=True,
                            type=date.my_fromisoformat,
                            help='Testcase start time in ISO 8601 format')
    parser_add.add_argument('--end', required=True,
                            type=date.my_fromisoformat,
                            help='Testcase end time in ISO 8601 format')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug(f"Args: {args}")

    junit = JUnitXmlPlus.fromfile_or_new(args.file)

    if args.action == 'print':
        print(junit.get_info())
    elif args.action == 'add':
        new = {
            'name': args.name,
            'result': args.result,
            'system-out': args.out,
            'system-err': args.err,
            'message': args.message,
            'start': args.start,
            'end': args.end,
        }
        junit.add_to_suite(args.suite, new)
    else:
        raise Exception('I do not know what to do')
