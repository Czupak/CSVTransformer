import argparse
import json
import sys
import pandas as pd
import regex as re


class CSVConv:

    def __init__(self, debug=False):
        self.debug = debug
        self.params = {}
        self.df = None
        self._possible_params = [
            'input_file', 'output_file', 'output_header', 'sort_by',
            'input_header', 'delimiter', 'header_from_file_name', 'header_map'
        ]

    def print(self, msg):
        if self.debug:
            print(msg)

    def process_header_from_file_name(self):
        if self.params['header_from_file_name'] is not None:
            for col in self.params['header_from_file_name'].keys():
                regex = self.params['header_from_file_name'][col]
                reg_res = re.match(regex, self.params['input_file'])
                if reg_res:
                    self.df[col] = reg_res[1]
                else:
                    self.df[col] = 'No match'

    def process_header_map(self):
        if self.params['header_map'] is not None:
            for col in self.params['header_map'].keys():
                if self.params['header_map'][col] is not None:
                    self.df = self.df.rename(
                        columns={self.params['header_map'][col]: col})
                else:
                    self.df[col] = ''

    def read_json_params(self, json_file):
        self.print(f'Reading {json_file}...')
        try:
            with open(json_file, 'r') as fh:
                params = json.load(fh)
                for key in params.keys():
                    self.set_param(key, params[key])
        except Exception as e:
            sys.exit(e)

    def set_param(self, param, value):
        if param not in self._possible_params:
            sys.exit(f'{param} not supported')
        self.params[param] = value

    def set_params(self,
                   input_file,
                   output_file,
                   output_header,
                   sort_by,
                   input_header=(),
                   delimiter=',',
                   header_from_file_name=None,
                   header_map=None):
        self.params = {}
        self.df = None
        for param in self._possible_params:
            self.set_param(locals().get(param, None))

    def validate_params(self):
        for param in self._possible_params:
            if param not in self.params.keys():
                sys.exit(f'Missing {param}!')

    def convert(self):
        self.validate_params()
        self.print(f'Reading from {self.params["input_file"]}...')
        kw_args = {'delimiter': self.params['delimiter']}
        if len(self.params['input_header']) > 0:
            kw_args['names'] = self.params['input_header']
        self.df = pd.read_csv(self.params['input_file'], **kw_args)
        self.print("Converting...")
        self.process_header_from_file_name()
        self.process_header_map()
        self.df = self.df[self.params['output_header']].reset_index(drop=1)
        self.df = self.df.sort_values(by=self.params['sort_by'])
        self.print(f"Writing to {self.params['output_file']}...")
        self.df.to_csv(self.params['output_file'], index=False)
        self.print(f'Done!')


def get_options():
    args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Example: python csv_transformer.py -p profile.json [-i input.csv] [-o output.csv] [-v]")
    parser.add_argument("-p",
                        "--profile",
                        help="JSON Profile file",
                        required=True)
    parser.add_argument("-i",
                        "--input",
                        help="CSV input file")
    parser.add_argument("-o",
                        "--output",
                        help="CSV output file")
    parser.add_argument("-v",
                        "--verbose",
                        dest='verbose',
                        action='store_true',
                        help="Verbose mode.")
    return parser.parse_args(args)


if __name__ == '__main__':
    options = get_options()
    if options.profile:
        converter = CSVConv(debug=options.verbose)
        converter.read_json_params(options.profile)
        if options.input:
            converter.set_param('input_file', options.input)
        if options.output:
            converter.set_param('output_file', options.output)
        converter.convert()
