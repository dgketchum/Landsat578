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
from .usgs_download import get_candidate_scenes_list, down_usgs_by_list
from datetime import datetime, timedelta

"""
Get a scenes list for download_usgs and prep the pymetric directory structure.

output should be of form: ['LT50430302007147PAC01', 'LT50430302007131PAC01']
"""


def pymetric_preparation(clear_scenes, pymetric_root, usgs_creds):
    scenes_list = []
    years = []
    paths = []
    rows = []

    lst = read_csv(clear_scenes, header=None).iloc[:, 0].tolist()
    for item in lst:
        sat = item[:4].replace('0', '')
        dt = datetime.strptime(item[-8:], '%Y%m%d')
        start = dt - timedelta(days=1)
        end = dt + timedelta(days=1)
        path, row = item[5:8], item[8:11]
        if start.year not in years:
            years.append(start.year)
        if path not in paths:
            paths.append(path.lstrip('0'))
        if row not in rows:
            rows.append(row.lstrip('0'))

        scene = get_candidate_scenes_list(path, row, sat, start, end)
        scenes_list.append(scene[0])

    orgainize_directory(pymetric_root, paths, rows, years)
    for scene, name in zip(scenes_list, lst):
        out = os.path.join(pymetric_root, 'landsat', scene[3:6].lstrip('0'), scene[6:9].lstrip('0'),
                           scene[9:13])
        down_usgs_by_list(list([scene]), output_dir=out,
                          usgs_creds_txt=usgs_creds, zipped=True,
                          alt_name=name)
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
