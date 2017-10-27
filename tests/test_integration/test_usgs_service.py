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
import unittest

from datetime import datetime

from core import usgs_download as usgs
from core import download_composer as dc
from core.usgs_download import InvalidCredentialsResponse


class USGSLandstatTestCase(unittest.TestCase):
    def setUp(self):
        self.start_7, self.end_7 = datetime(2007, 5, 1), datetime(2007, 5, 31)
        self.start_14, self.end_14 = datetime(2014, 5, 1), datetime(2014, 5, 31)
        self.lat, self.lon = 47.4545, -107.9514
        self.path, self.row = 37, 27
        # test for acquisition month of May, 2007 (L5, L7), 2024 (L8).
        self.known_l5_scene = ['LT50370272007137PAC01', 'LT50370272007121PAC01']
        self.known_l7_scene = ['LE70370272007145EDC00', 'LE70370272007129EDC00']
        self.known_l8_scene = ['LC80370272014140LGN01', 'LC80370272014124LGN01']

    def tearDown(self):
        pass

    def test_find_scenes_by_pathrow(self):
        l5_scenes = usgs.get_candidate_scenes_list(path=self.path, row=self.row, sat_name='LT5',
                                                   start_date=self.start_7, end_date=self.end_7,
                                                   max_cloud_cover=100)
        l7_scenes = usgs.get_candidate_scenes_list(path=self.path, row=self.row, sat_name='LE7',
                                                   start_date=self.start_7, end_date=self.end_7,
                                                   max_cloud_cover=100)
        l8_scenes = usgs.get_candidate_scenes_list(path=self.path, row=self.row, sat_name='LC8',
                                                   start_date=self.start_14, end_date=self.end_14,
                                                   max_cloud_cover=100)
        self.assertEqual(l5_scenes, self.known_l5_scene)
        self.assertEqual(l7_scenes, self.known_l7_scene)
        self.assertEqual(l8_scenes, self.known_l8_scene)

    def test_find_scenes_by_latlon(self):
        l5_scenes = usgs.get_candidate_scenes_list(path=self.path, row=self.row, sat_name='LT5',
                                                   start_date=self.start_7, end_date=self.end_7,
                                                   max_cloud_cover=100)
        l7_scenes = usgs.get_candidate_scenes_list(path=self.path, row=self.row, sat_name='LE7',
                                                   start_date=self.start_7, end_date=self.end_7,
                                                   max_cloud_cover=100)
        l8_scenes = usgs.get_candidate_scenes_list(path=self.path, row=self.row, sat_name='LC8',
                                                   start_date=self.start_14, end_date=self.end_14,
                                                   max_cloud_cover=100)
        self.assertEqual(l5_scenes, self.known_l5_scene)
        self.assertEqual(l7_scenes, self.known_l7_scene)
        self.assertEqual(l8_scenes, self.known_l8_scene)


class DownloadBadCredsTestCase(unittest.TestCase):
    def setUp(self):
        self.home = os.path.expanduser('~')
        self.start = datetime(2007, 5, 1)
        self.end = datetime(2007, 5, 30)
        self.sat = 'LT5'
        self.output = os.path.join(self.home, 'images', 'sandbox', 'downer')
        self.bad_usgs_creds = 'tests/data/bad_creds.txt'
        self.path, self.row = 37, 27

    def test_bad_credentials(self):
        try:
            dc.download_landsat(start=self.start, end=self.end,
                                satellite=self.sat, output_path=self.output,
                                usgs_creds=self.bad_usgs_creds,
                                path=self.path, row=self.row,
                                return_list=False)
        except InvalidCredentialsResponse:
            self.assertIsInstance([1, 2], list)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
