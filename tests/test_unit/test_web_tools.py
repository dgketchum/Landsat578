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

import unittest
from datetime import datetime

from core import web_tools


class WebToolsTestCase(unittest.TestCase):
    def setUp(self):

        self.known_scene_l5 = 'LT50370272007121PAC01'
        self.bad_scene5 = 'LT50370272007122PAC01'
        self.known_scene_l7 = 'LE70370272007129EDC00'
        self.bad_scene7 = 'LE70370272007122EDC00'
        self.known_scene_l8 = 'LC80370272014124LGN01'
        self.bad_scene8 = 'LC80370272014122LGN01'
        # known overpasses for pr 37, 27
        self.path, self.row = 37, 27
        self.overpass_l5 = datetime(2007, 5, 17)
        self.overpass_l7 = datetime(2007, 5, 25)
        self.overpass_l8 = datetime(2014, 5, 20)
        self.search_start = datetime(2007, 5, 16)
        # known centroid of pr 37, 27
        self.lat, self.lon = 47.45, -107.951

    def tearDown(self):
        pass

    def test_wrs2_latlon_convert(self):
        expect_latlon = web_tools.convert_lat_lon_wrs2pr(self.path, self.row, conversion_type='convert_pr_to_ll')
        self.assertEqual(self.lat, expect_latlon[0])
        self.assertEqual(self.lon, expect_latlon[1])

        expect_pr = web_tools.convert_lat_lon_wrs2pr(self.lat, self.lon)
        self.assertTrue([self.path, self.row], [expect_pr])


if __name__ == '__main__':
    unittest.main()

# ==================================================================================
