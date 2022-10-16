import argparse
import glob
import json
import sys
import os
import pandas as pd
import re


class CSVConv:

    def __init__(self,
                 profile=None,
                 input=None,
                 input_dir=None,
                 output=None,
                 output_dir=None,
                 silent=False):
        self.profile = profile
        self.input_file = input
        self.input_dir = input_dir
        self.output_file = output
        self.output_dir = output_dir
        self.silent = silent

        self.params = {}
        self.read_json_params()
        self.validate_params()

        self.df = None

    def print(self, msg, lvl=0):
        if not self.silent:
            print(f'{lvl*" "}{msg}')

    def process_header_from_file_name(self, file_name):
        if self.params['header_from_file_name'] is not None:
            for col in self.params['header_from_file_name'].keys():
                regex = self.params['header_from_file_name'][col]
                reg_res = re.match(regex, file_name)
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

    def read_json_params(self):
        self.print(f'Reading {self.profile}...')
        try:
            with open(self.profile, 'r') as fh:
                self.params = json.load(fh)
        except Exception as e:
            sys.exit(e)

    def _get_param_if_exist(self, param):
        if param in self.params.keys() and self.params[param] not in [
                None, ""
        ]:
            return self.params[param]
        return None

    def validate_params(self):
        for param in ['input_file', 'input_dir', 'output_file', 'output_dir']:
            val = self._get_param_if_exist(param)
            setattr(self, param, val)

    def convert_one(self, input_file, output_file):
        self.print(f'[CSV] Reading from {input_file}...', 2)
        kw_args = {'delimiter': self.params['delimiter']}
        if len(self.params['input_header']) > 0:
            kw_args['names'] = self.params['input_header']
        self.df = pd.read_csv(input_file, **kw_args)
        self.print("Converting...", 4)
        self.process_header_from_file_name(input_file)
        self.process_header_map()
        self.df = self.df[self.params['output_header']].reset_index(drop=1)
        self.df = self.df.sort_values(by=self.params['sort_by'])

        output_types = self._get_param_if_exist('output_types')
        if output_types is None:
            output_types = ["csv"]
        for type in output_types:
            if type == 'csv':
                self.print(f"[CSV] Writing to {output_file}...", 2)
                with open(output_file, 'w') as fh:
                    fh.write('sep=,\n')
                self.df.to_csv(output_file, index=False, mode='a')
            if type == 'xlsx':
                xls_file = os.path.splitext(output_file)[0] + ".xlsx"
                self.print(f"[XLSX] Writing to {xls_file}...", 2)
                self.df.to_excel(xls_file, index=False)

    def convert(self):
        if self.input_dir is not None:
            if not os.path.exists(self.input_dir):
                sys.exit(f'Path does not exist: [input_dir={self.input_dir}]!')
            csv_files = glob.glob(os.path.join(self.input_dir, '*.csv'))
            counter = 0
            for csv_file in sorted(csv_files):
                counter += 1
                self.print(f'{counter}/{len(csv_files)}', 2)
                out_file = os.path.join(self.output_dir,
                                        os.path.basename(csv_file))
                self.convert_one(csv_file, out_file)
        else:
            self.print(f'1/1', 2)
            self.convert_one(self.input_file, self.output_file)

        self.print(f'Done!')


def get_options():
    args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Example: python csv_transformer.py -p profile.json "
        "[-i input.csv] [-o output.csv] [-id input_dir] [-od output_dir] [-v]")
    parser.add_argument("-p",
                        "--profile",
                        help="JSON Profile file",
                        required=True)
    parser.add_argument("-i", "--input", help="CSV input file")
    parser.add_argument("-o", "--output", help="CSV output file")
    parser.add_argument("-id",
                        "--input_dir",
                        help="Directory with CSV input files")
    parser.add_argument("-od",
                        "--output_dir",
                        help="Directory for CSV output files")
    parser.add_argument("-s",
                        "--silent",
                        dest='silent',
                        action='store_true',
                        help="Silent mode.")
    return parser.parse_args(args)


if __name__ == '__main__':
    options = get_options()
    kwargs = {}
    for param in [
            'silent', 'profile', 'input', 'output', 'input_dir', 'output_dir'
    ]:
        kwargs[param] = getattr(options, param)
    converter = CSVConv(**kwargs)
    converter.convert()
