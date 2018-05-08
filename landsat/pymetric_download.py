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
import sys
sys.path.append(os.path.dirname(__file__))
from pandas import read_csv
from datetime import datetime, timedelta
from itertools import product
from copy import deepcopy

from landsat.google_download import GoogleDownload

"""
Download into pymetric directory structure i.e. pymetric_root/landsat/path/row/year
w/ naming e.g. LC08_041027_20150228.tar.gz
"""

fmt_1 = '%Y%m%d'
fmt_2 = '%Y-%m-%d'


def download(clear_scenes, pymetric_root):
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

        dt = datetime.strptime(item[-8:], fmt_1)
        if dt.year not in years:
            years.append(dt.year)
        dates.append(dt)
        path, row = item[5:8], item[8:11]
        if path not in paths:
            paths.append(path)
        if row not in rows:
            rows.append(row)

    start = datetime.strftime(min(dates) - timedelta(days=1), fmt_2)
    end = datetime.strftime(max(dates) + timedelta(days=1), fmt_2)

    objects = list(product(sats, paths, rows, years))

    organize_directory(pymetric_root, objects)

    for item in objects:
        sat, p, r, y = item
        out = os.path.join(pymetric_root, 'landsat', str(p), str(r), str(y))
        g = GoogleDownload(start, end, sat, path=p, row=r, output_path=out, alt_name=True)

        included_scenes = deepcopy(g.pymetric_ids)
        for scene in included_scenes:
            if scene not in lst:
                print('remove {}'.format(scene))
                g.scenes_df = g.scenes_df[g.scenes_df.PYMETRIC_ID != scene]

        g.download()
    return None


def organize_directory(pymetric_rt, p_r_yr_combinations):
    root_list = os.listdir(pymetric_rt)
    landsat = os.path.join(pymetric_rt, 'landsat')
    if 'landsat' not in root_list:
        print('Making landsat dir in {}'.format(pymetric_rt))
        os.mkdir(landsat)

    for item in p_r_yr_combinations:
        sat, p, r, y = item
        dst_dir = os.path.join(landsat, str(p), str(r), str(y))
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
