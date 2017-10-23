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

from core import usgs_download
from core.web_tools import convert_lat_lon_wrs2pr


class InvalidPathRowData(Exception):
    pass


def download_landsat(start, end, satellite, latitude=None, longitude=None,
                     path=None, row=None, output_path=None,
                     usgs_creds=None, dry_run=False, zipped=False):
    if path:
        image_index = [(path, row)]

    elif latitude and longitude:
        image_index = [convert_lat_lon_wrs2pr(latitude, longitude)]

    else:
        raise InvalidPathRowData('Must give path/row tuple, lat/lon tuple plus row/path \n'
                                 'shapefile, or a path/rows shapefile!')
    for tile in image_index:

        scenes_list = usgs_download.get_candidate_scenes_list(path_row=tile,
                                                              sat_name=satellite,
                                                              start_date=start,
                                                              end_date=end)
        if not scenes_list:
            print('No scenes for {} between {} and {}.'.format(satellite,
                                                               datetime.strftime(start,
                                                                                 '%Y-doy %j'),
                                                               datetime.strftime(end,
                                                                                 '%Y-doy %j')))

        elif dry_run:

            print(scenes_list)

            return scenes_list

        else:
            if output_path is None:
                output_path = os.getcwd()
                print('using current working dir as output_path={}'.format(output_path))

            if os.path.isdir(output_path):
                destination_path = os.path.join(output_path, '{}_{}_{}'.format(
                    satellite, tile[0], tile[1]))

                if not os.path.exists(destination_path):
                    print('making dir: {}'.format(destination_path))
                    os.makedirs(destination_path)

                usgs_download.down_usgs_by_list(scenes_list, destination_path,
                                                usgs_creds, zipped)
            else:
                print('invalid output directory. "{}" does not exist'.format(output_path))



if __name__ == 'main':
    pass

# ===============================================================================
