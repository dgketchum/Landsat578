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

from core import download_composer as dc


class DownloadTestCase(unittest.TestCase):
    def setUp(self):
        self.home = os.path.expanduser('~')
        self.start = datetime(2007, 5, 1)
        self.end = datetime(2007, 5, 30)
        self.sat = 'LT5'
        self.output = os.path.join(self.home, 'images', 'sandbox', 'downer')
        self.usgs_creds = os.path.join(self.home, 'images', 'usgs.txt')
        self.path, self.row = 37, 27
        self.known_scene = ['LT50370272007121PAC01', 'LT50370272007137PAC01']

    def tearDown(self):
        pass

    def test_scene_list(self):
        scene_list = dc.download_landsat(self.start, self.end, self.sat,
                                         path=self.path, row=self.row,
                                         dry_run=True)
        self.assertEqual(self.known_scene, scene_list)

    # can't run the download test on travis.

    # def test_downloader(self):
    #     dc.download_landsat((self.start, self.end),
    #                         self.sat, output_path=self.output,
    #                         usgs_creds=self.usgs_creds,
    #                         path_row_list=[(self.path, self.row)],
    #                         dry_run=False)
    #     sub_folder = os.path.join(self.output, 'LT5_37_27', 'LT50370272007121PAC01')
    #     files = os.listdir(sub_folder)
    #     known = ['LT50370272007121PAC01_B1.TIF', 'LT50370272007121PAC01_B2.TIF', 'LT50370272007121PAC01_B3.TIF',
    #              'LT50370272007121PAC01_B4.TIF', 'LT50370272007121PAC01_B5.TIF', 'LT50370272007121PAC01_B6.TIF',
    #              'LT50370272007121PAC01_B7.TIF', 'LT50370272007121PAC01_GCP.txt', 'LT50370272007121PAC01_MTL.txt',
    #              'LT50370272007121PAC01_VER.jpg', 'LT50370272007121PAC01_VER.txt', 'README.GTF']
    #     self.assertEqual(files, known)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
