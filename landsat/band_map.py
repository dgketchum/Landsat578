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


class BandMap:
    def __init__(self):
        pass

    @property
    def selected(self):
        band_mapping = {'LC8': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
                        'LE7': ['1', '2', '3', '4', '5', '6_VCID_1', '6_VCID_2', '7', '8'],
                        'LT5': ['1', '2', '3', '4', '5', '6', '7']}
        return band_mapping

    @property
    def file_suffixes(self):
        b = {'LANDSAT_1': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_2': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_3': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_4': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_5': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],

             'LANDSAT_7': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF',
                           'B6_VCID_1.TIF', 'B6_VCID_2.TIF', 'B7.TIF', 'B8.TIF', 'MTL.txt'],

             'LANDSAT_8': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF',
                           'B7.TIF', 'B8.TIF', 'B9.TIF', 'B10.TIF', 'B11.TIF', 'BQA.TIF', 'MTL.txt']}
        return b


if __name__ == '__main__':
    home = os.path.expanduser('~')


# ========================= EOF ================================================================
