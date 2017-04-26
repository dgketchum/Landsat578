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

from landsat import usgs_download as usgs
from landsat import web_tools as wt


class USGSLandstatTestCase(unittest.TestCase):
    def setUp(self):
        self.start_7, self.end_7 = datetime(2007, 05, 01), datetime(2007, 05, 31)
        self.start_14, self.end_14 = datetime(2014, 05, 01), datetime(2014, 05, 31)

        self.lat, self.lon = 47.4545, -107.9514
        self.known_pathrow = 37, 27
        # test for acquisition month of May, 2007 (L5, L7), 2024 (L8).
        self.known_l5_scene = ['LT50370272007121PAC01', 'LT50370272007137PAC01']
        self.known_l7_scene = ['LE70370272007129EDC00', 'LE70370272007145EDC00']
        self.known_l8_scene = ['LC80370272014124LGN01', 'LC80370272014140LGN01']

    def tearDown(self):
        pass

    def test_find_scenes_by_pathrow(self):
        l5_scenes = usgs.get_candidate_scenes_list(self.known_pathrow, 'LT5', self.start_7, self.end_7)
        l7_scenes = usgs.get_candidate_scenes_list(self.known_pathrow, 'LE7', self.start_7, self.end_7)
        l8_scenes = usgs.get_candidate_scenes_list(self.known_pathrow, 'LC8', self.start_14, self.end_14)
        print l5_scenes
        print l7_scenes
        print l8_scenes
        self.assertEqual(l5_scenes, self.known_l5_scene)
        self.assertEqual(l7_scenes, self.known_l7_scene)
        self.assertEqual(l8_scenes, self.known_l8_scene)

    def test_find_scenes_by_latlon(self):
        ll = wt.convert_lat_lon_wrs2pr(self.lat, self.lon, conversion_type='convert_ll_to_pr')
        l5_scenes = usgs.get_candidate_scenes_list(ll, 'LT5', self.start_7, self.end_7)
        l7_scenes = usgs.get_candidate_scenes_list(ll, 'LE7', self.start_7, self.end_7)
        l8_scenes = usgs.get_candidate_scenes_list(ll, 'LC8', self.start_14, self.end_14)
        self.assertEqual(l5_scenes, self.known_l5_scene)
        self.assertEqual(l7_scenes, self.known_l7_scene)
        self.assertEqual(l8_scenes, self.known_l8_scene)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
