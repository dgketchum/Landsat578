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
from pandas import read_pickle
from datetime import datetime as dt

from update_landsat_metadata import update

SATS = ['LANDSAT_1', 'LANDSAT_2', 'LANDSAT_3', 'LANDSAT_4',
        'LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']
fmt = '%Y-%m-%d'


def get_candidate_scenes_list(path, row, sat_number, start_date, end_date, max_cloud_cover=70):

    start, end = dt.strptime(start_date, fmt), dt.strptime(end_date, fmt)
    scenes_path = check_scenes_lists(sat_number)
    df = read_pickle(scenes_path)
    df = df.loc[(df.CLOUD_COVER < max_cloud_cover) & (df.WRS_PATH == path) & (df.WRS_ROW == row)
                & (start < df.DATE_ACQUIRED) & (df.DATE_ACQUIRED < end)]
    url_list = df.BASE_URL.values.tolist()
    # TODO: Filter out pre-collection urls before downloading
    pass


def check_scenes_lists(sat):
    abspath = os.path.abspath(os.path.dirname(__file__).replace('landsat', 'scene_list'))
    list_dir = [x for x in os.listdir(abspath)]
    sats = ['LANDSAT_1', 'LANDSAT_2', 'LANDSAT_3', 'LANDSAT_4', 'LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']
    for s in sats:
        if s not in list_dir:
            update()
    path = os.path.join(abspath, 'LANDSAT_{}'.format(sat))
    return path


if __name__ == '__main__':
    home = os.path.expanduser('~')
    get_candidate_scenes_list(39, 27, 8, '2013-05-01', '2013-10-21', max_cloud_cover=20)

# ========================= EOF ================================================================
