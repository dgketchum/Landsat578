#!/usr/bin/env python

# ===============================================================================
# Copyright 2017 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import os
import argparse
import sys
import yaml
from datetime import datetime

try:
    from .download_composer import download_landsat

except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from .download_composer import download_landsat

try:
    from .pymetric_prep import pymetric_preparation

except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from .pymetric_prep import pymetric_preparation


class TooFewInputsError(Exception):
    pass


DEFAULT_CFG = '''
# date format: 'YYYY-MM-DD'
start: '2007-05-01'
end: '2007-05-31'
path: 43
row: 30
latitude:
longitude:
output_path: None
satellite: LT5
usgs_creds: /path/to/usgs_creds.txt
# pymetric directory structure: e.g. D:/pyMETRIC/harney/landsat/path/row/year
# mutually exclusive with output, put None if output is specified, and zipped: True
pymetric_root: D:/pyMETRIC/root
clear_scenes: D:/pyMETRIC/misc/clear_scenes.txt
return_list: False
zipped: False
max_cloud_percent: 100
'''


def create_parser():
    parser = argparse.ArgumentParser(prog='landsat', description='Download and unzip landsat data.')

    parser.add_argument('--satellite', help='Satellite name: LT5, LE7, or LC8')
    parser.add_argument('--start', help='Start date in format YYYY-MM-DD')
    parser.add_argument('--end', help='End date in format YYYY-MM-DD')
    parser.add_argument('-lat', '--latitude', help='Latitude, decimal degrees', type=str)
    parser.add_argument('-lon', '--longitude', help='Longitude, decimal degrees', type=str)
    parser.add_argument('-p', '--path', help='The path')
    parser.add_argument('-r', '--row', help='The row')
    parser.add_argument('-o', '--output', help='Output directory', default=os.getcwd())
    parser.add_argument('-cred', '--credentials',
                        help='Path to a text file with USGS credentials with one space between <username password>')

    parser.add_argument('-conf', '--configuration', help='Path to your configuration file. If a directory is provided,'
                                                         'a template cofiguration file will be created there.')
    parser.add_argument('-cs', '--clear-scenes', help='Path to your clear scenes file.')
    parser.add_argument('-pym', '--pymetric-root', help='Path to your pyMETRIC study area root dir.')

    parser.add_argument('--return-list', help='Just return list of images without downloading', action='store_true',
                        default=False)

    parser.add_argument('--zipped', help='Download .tar.gz file(s), without unzipping',
                        action='store_true', default=False)

    parser.add_argument('--max-cloud-percent', help='Maximum percent of of image obscured by clouds accepted,'
                                                    ' type integer',
                        default=100)

    return parser


def main(args):
    if args:
        print(args)

        fmt = '%Y-%m-%d'

        cfg = {'output_path': args.output,
               'usgs_creds': args.credentials,
               'return_list': args.return_list,
               'zipped': args.zipped}

        if args.configuration:
            if os.path.isdir(args.configuration):
                print('Creating template configuration file at {}.'.format(args.configuration))
                check_config(args.configuration)

            print('\nStarting download with configuration file {}'.format(args.configuration))
            with open(args.configuration, 'r') as rfile:
                ycfg = yaml.load(rfile)
                cfg.update(ycfg)
            if cfg['pymetric_root']:
                pymetric_preparation(cfg['clear_scenes'], cfg['pymetric_root'],
                                     cfg['usgs_creds'])
            else:
                cfg['start'] = datetime.strptime(cfg['start'], fmt)
                cfg['end'] = datetime.strptime(cfg['end'], fmt)
                scenes = download_landsat(**cfg)

        if not args.configuration:
            if not args.start:
                raise TooFewInputsError('Must specify path and row, or latitude and longitude, '
                                        'or the path to file with one of these pairs')
            start = datetime.strptime(args.start, fmt)
            end = datetime.strptime(args.end, fmt)
            sat = args.satellite

            if args.latitude:
                print('\nStarting download with latlon...')
                cfg['latitude'] = args.latitude
                cfg['longitude'] = args.longitude
                scenes = download_landsat(start, end, sat, **cfg)

            elif args.path:
                print('\nStarting download with pathrow...')
                cfg['path'] = args.path
                cfg['row'] = args.row
                scenes = download_landsat(start, end, sat, **cfg)

        if cfg['return_list']:
            return scenes


def cli_runner():
    parser = create_parser()
    args = parser.parse_args()
    return main(args)


def check_config(dirname):
    path = os.path.join(dirname, 'downloader_config.yml')
    print('\n*****A default config file {} will be written'.format(path))

    with open(path, 'w') as wfile:
        print('-------------- DEFAULT CONFIG -----------------')
        print(DEFAULT_CFG)
        print('-----------------------------------------------')
        wfile.write(DEFAULT_CFG)

    print('***** Please edit the config file at {} and run the downer again *****\n'.format(
        dirname))

    sys.exit()


if __name__ == '__main__':
    cli_runner()

# ===============================================================================
