# =============================================================================================
# Copyright 2018 dgketchum
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
# =============================================================================================

import os
from pandas import read_csv
from datetime import datetime
from itertools import product

from .google_download import GoogleDownload

"""
Get a scenes list for download_usgs and prep the pymetric directory structure.

output should be of form: ['LT50430302007147PAC01', 'LT50430302007131PAC01']
"""


def pymetric_download(clear_scenes, pymetric_root):
    dates = []
    years = []
    paths = []
    rows = []
    sats = []

    lst = read_csv(clear_scenes, header=None).iloc[:, 0].tolist()
    for item in lst:
        sat = int(item[3])
        if sat not in sats:
            sats.append(sat)

        dt = datetime.strptime(item[-8:], '%Y%m%d')
        if dt.year not in years:
            years.append(dt.year)
        dates.append(dt)

    start = min(dates)
    end = max(dates)

    orgainize_directory(pymetric_root, paths, rows, years)

    objects = list(product(sats, paths, rows, years))
    for s, p, r, y in objects:
        out = os.path.join(pymetric_root, 'landsat', scene[3:6].lstrip('0'), scene[6:9].lstrip('0'),
                   scene[9:13])
        g = GoogleDownload(start, end, s, path=p, row=r,
                           output_path=os.path.join(pymetric_root, p, r, y),
                           alt_name=out)

    return None


def orgainize_directory(pymetric_rt, paths, rows, years):
    root_list = os.listdir(pymetric_rt)
    landsat = os.path.join(pymetric_rt, 'landsat')
    if 'landsat' not in root_list:
        print('Making landsat dir in {}'.format(pymetric_rt))
        os.mkdir(landsat)
    for path in paths:
        for row in rows:
            for year in years:
                dst_dir = os.path.join(landsat, str(path), str(row),
                                       str(year))
                try:
                    os.makedirs(dst_dir)
                    print('Made {}'.format(dst_dir))
                except Exception as e:
                    print('Exception {}'.format(e))
                    print('...skipping creation...')
                    pass


if __name__ == '__main__':
    home = os.path.expanduser('~')

# ========================= EOF ====================================================================
