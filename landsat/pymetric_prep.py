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
from .usgs_download import get_candidate_scenes_list
from datetime import datetime

"""
Get a scenes list for download_usgs and prep the pymetric directory structure.

output should be of form: ['LT50430302007147PAC01', 'LT50430302007131PAC01']
"""


def pymetric_preparation(clear_scenes, pymetric_root):
    lst = read_csv(clear_scenes).iloc[:, 0].tolist()
    for item in lst:
        sat = item[:4].replace('0', '')
        dt = datetime.strptime(item[-8:], '%Y%m%d')

    get_candidate_scenes_list(path, row, sat_name, start_date, end_date, max_cloud_cover=70)
    pass


if __name__ == '__main__':
    home = os.path.expanduser('~')

# ========================= EOF ====================================================================
