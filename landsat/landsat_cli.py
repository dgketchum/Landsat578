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

from google_download import GoogleDownload
from pymetric_download import download
from update_landsat_metadata import update


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
satellite: 5

return_list: False
zipped: True
max_cloud_percent: 100

# pymetric directory structure: e.g. D:/pyMETRIC/harney/landsat/path/row/year
# using pymetric_root and clear_scenes overrides all other arguments
# leave both blank to disable

pymetric_root: D:/pyMETRIC/root
clear_scenes: D:/pyMETRIC/misc/clear_scenes.txt
'''

CONFIG_PLACEMENT = os.path.dirname(__file__)


def create_parser():
    parser = argparse.ArgumentParser(prog='landsat', description='Download and unzip landsat data.')

    parser.add_argument('--satellite', '-sat', help='Satellite number: 1-8, except 6', type=int)
    parser.add_argument('--start', help='Start date in format YYYY-MM-DD', type=str)
    parser.add_argument('--end', help='End date in format YYYY-MM-DD', type=str)
    parser.add_argument('-lat', '--latitude', help='Latitude, decimal degrees', type=float, default=None)
    parser.add_argument('-lon', '--longitude', help='Longitude, decimal degrees', type=float, default=None)
    parser.add_argument('-p', '--path', help='The path', type=str, default=None)
    parser.add_argument('-r', '--row', help='The row', type=str, default=None)
    parser.add_argument('-o', '--output-path', help='Output directory', default=CONFIG_PLACEMENT)

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

    parser.add_argument('--update-scenes', help='Update the scenes list this program uses to discover the '
                                                'latest imagery.', default=False)

    return parser


def main(args):
    return_scene_list = False

    if args:

        cfg = {}
        for arg in vars(args):
            var = getattr(args, arg)
            if var is not None:
                cfg[arg] = var

        if cfg['update_scenes']:
            update()

        if args.configuration:
            if os.path.isdir(args.configuration):
                print('Creating template configuration file at {}.'.format(args.configuration))
                check_config(args.configuration)

            with open(args.configuration, 'r') as rfile:
                ycfg = yaml.load(rfile)
                cfg.update(ycfg)

            if cfg['return_list']:
                return_scene_list = True

            del cfg['return_list']
            del cfg['configuration']
            del cfg['update_scenes']

            if cfg['pymetric_root']:
                download(cfg['clear_scenes'], cfg['pymetric_root'])
            else:
                del cfg['clear_scenes']
                del cfg['pymetric_root']

                g = GoogleDownload(**cfg)
                if return_scene_list:
                    return g.candidate_scenes(return_list=True)
                g.download()

        else:
            del cfg['return_list']
            del cfg['update_scenes']

            g = GoogleDownload(**cfg)
            if return_scene_list:
                return g.candidate_scenes(return_list=True)
            else:
                g.download()


def cli_runner():
    parser = create_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
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
