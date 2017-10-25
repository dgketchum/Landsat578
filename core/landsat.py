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
import logging
import os
import argparse
import sys
import yaml
from datetime import datetime


try:
    from core.frontmatter import frontmatter
    from core.download_composer import download_landsat
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.frontmatter import frontmatter
    from core.download_composer import download_landsat

SATNAMES = ('LT5', 'LE7', 'LC8')


def create_parser():
    parser = argparse.ArgumentParser(prog='landsat', description='Download and unzip landsat data.')

    parser.add_argument('satellite', help='Satellite name: {}'.format(','.join(SATNAMES)))
    parser.add_argument('start', help='Start date in format YYYY-MM-DD')
    parser.add_argument('end', help='End date in format YYYY-MM-DD')
    parser.add_argument('-lat', '--latitude', help='Latitude, decimal degrees', type=str)
    parser.add_argument('-lon', '--longitude', help='Longitude, decimal degrees', type=str)
    parser.add_argument('-p', '--path', help='The path')
    parser.add_argument('-r', '--row', help='The row')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-cred', '--credentials',
                        help='Path to a text file with USGS credentials with one space between <username password>')

    parser.add_argument('-conf', '--configuration', help='Path to your configuration file. If a directory is provided,'
                                                         'a template cofiguration file will be created there.')
    parser.add_argument('--return-list', help='Just return list of images without downloading', action='store_true',
                        default=False)

    parser.add_argument('--zipped', help='Download .tar.gz file(s), without unzipping',
                        action='store_true', default=False)
    parser.add_argument('--file', help=''),
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Display DEBUG level messages', default=False)

    return parser


def main(args):
    if args:
        logger = setup_logging(args.verbose)

        # the logger object does need to be passed around. if its needed in another module simply use
        # logger = logging.getLogger()

        logger.debug(args)

        fmt = '%Y-%m-%d'

        def check_date(d):
            try:
                return datetime.strptime(d, fmt)
            except ValueError,e:
                logger.critical(e)
                logger.critical('Invalid start date. Must be in YYYY-MM-DD')

        start = check_date(args.start)
        if not start:
            return
        end = check_date(args.end)
        if not end:
            return

        sat = args.satellite
        if sat not in SATNAMES:

            logger.critical('Invalid Satellite name: {}. Must be {}'.format(sat, SATNAMES))
            return

        cfg = {'output_path': args.output,
               'usgs_cred': args.credentials,
               'dry_run': args.return_list,
               'zipped': args.zipped}

        if args.file:
            logger.info('Starting download with configuration file {}'.format(args.file))
            # print('\nStarting download with configuration file {}'.format(args.file))
            with open(args.file, 'r') as rfile:
                ycfg = yaml.load(rfile)
                cfg.update(ycfg)
        elif args.latitude:
            logger.info('Starting download with latlon...')
            cfg['latitude'] = args.latitude
            cfg['longitude'] = args.longitude
        elif args.path:
            logger.info('Starting download with pathrow...')
            # print('\nStarting download with pathrow...')
            cfg['path'] = args.path
            cfg['row'] = args.row

        else:
            logger.critical('Invalid args. Need to specify at least one of the following: path, lat or file')
            # print('invalid args. Need to specify at least one of the following: path, lat or file')
            return

        scenes = download_landsat(start, end, sat, **cfg)
        return scenes


def setup_logging(verbose=False):
    logger = logging.getLogger()
    if verbose:
        logger.setLevel(logging.DEBUG)

    h = logging.StreamHandler()

    fmt = '%(name)-10s: %(asctime)s %(levelname)-9s %(message)s'
    h.setFormatter(logging.Formatter(fmt))
    logger.addHandler(h)

    return logger


def cli_runner():
    frontmatter()
    parser = create_parser()
    args = parser.parse_args()
    return main(args)


if __name__ == '__main__':
    cli_runner()

# ===============================================================================
