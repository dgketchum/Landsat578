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

from landsat import download_composer


class DownloadTestCase(unittest.TestCase):
    def setUp(self):
        self.home = os.path.expanduser('~')
        self.start = datetime(2007, 5, 1)
        self.end = datetime(2007, 5, 30)
        self.sat = 'LT5'
        self.output = os.path.join(self.home, 'images', self.sat)
        self.usgs_creds = os.path.join(self.home, 'images', 'usgs.txt')
        self.path_row = 37, 27
        self.known_scene = ['LT50370272007121PAC01', 'LT50370272007137PAC01']

    def tearDown(self):
        pass

    def test_downer(self):
        scene_list = download_composer.download_landsat((self.start, self.end), self.sat,
                                                        path_row_tuple=self.path_row, dry_run=True)
        self.assertEqual(self.known_scene, scene_list)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
