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
from datetime import datetime

from .usgs_download import get_candidate_scenes_list, down_usgs_by_list
from .web_tools import convert_lat_lon_wrs2pr


class InvalidPathRowData(Exception):
    pass


def download_landsat(start=None, end=None, satellite=None, latitude=None, longitude=None,
                     path=None, row=None, output_path=None,
                     usgs_creds=None, return_list=False, zipped=False, max_cloud_percent=100):
    if path:
        pass

    elif latitude and longitude:
        path, row = convert_lat_lon_wrs2pr(latitude, longitude)

    else:
        raise InvalidPathRowData('Must give path/row tuple, lat/lon tuple plus row/path \n'
                                 'shapefile, or a path/rows shapefile!')

    scenes_list = get_candidate_scenes_list(path=path, row=row, sat_name=satellite, start_date=start,
                                            end_date=end, max_cloud_cover=max_cloud_percent)
    if not scenes_list:
        print('No scenes for {} between {} and {}.'.format(satellite,
                                                           datetime.strftime(start,
                                                                             '%Y-doy %j'),
                                                           datetime.strftime(end,
                                                                             '%Y-doy %j')))
        return None

    elif return_list:

        print(scenes_list)

        return scenes_list

    else:

        destination_path = os.path.join(output_path, '{}_{}_{}'.format(
            satellite, path, row))

        if not os.path.exists(destination_path):
            print('making dir: {}'.format(destination_path))
            os.makedirs(destination_path)

        down_usgs_by_list(scenes_list, destination_path, usgs_creds, zipped)

        return None


if __name__ == 'main':
    pass

# ===============================================================================
