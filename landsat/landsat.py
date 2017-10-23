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

import argparse
from datetime import datetime

from landsat.download_composer import download_landsat


def create_parser():

    parser = argparse.ArgumentParser(prog='landsat', description='Download and unzip landsat data.')

    parser.add_argument('satellite', help='Satellite name: LT5, LE7, or LC8')
    parser.add_argument('start', help='Start date in format YYYY-MM-DD')
    parser.add_argument('end', help='End date in format YYYY-MM-DD')
    parser.add_argument('--lat', help='Latitude, decimal degrees', type=str)
    parser.add_argument('--lon', help='Longitude, decimal degrees', type=str)
    parser.add_argument('--path', help='The path')
    parser.add_argument('--row', help='The row')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('--credentials',
                        help='Path to a text file with USGS credentials with one space between <username password>')
    parser.add_argument('--return-list', help='Just return list of images without downloading', action='store_true',
                        default=False)

    return parser


def main(args):
    if args:
        if args.lat:
            print('\nStarting download with latlon...')
            print(args)
            scenes = download_landsat(
                (datetime.strptime(args.start, '%Y-%m-%d'), datetime.strptime(args.end, '%Y-%m-%d')),
                args.satellite, latitude=args.lat, longitude=args.lon, output_path=args.output,
                usgs_creds=args.credentials, dry_run=args.return_list)

            return scenes

        elif args.path:
            print('\nStarting download with pathrow...')
            print(args)
            scenes = download_landsat(
                (datetime.strptime(args.start, '%Y-%m-%d'), datetime.strptime(args.end, '%Y-%m-%d')),
                args.satellite, path_row_list=[(args.path, args.row)], output_path=args.output,
                usgs_creds=args.credentials, dry_run=args.return_list)

            return scenes

        else:
            raise NotImplementedError('Was not executed.')


def __main__():

    global parser
    parser = create_parser()
    args = parser.parse_args()
    exit(main(args))


if __name__ == '__main__':
    try:
        __main__()

    except KeyboardInterrupt:
        exit(1)

# ===============================================================================
