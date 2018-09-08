# ===============================================================================
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
# ===============================================================================
import os
import unittest

from landsat.google_download import GoogleDownload


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.start = '2013-05-15'
        self.end = '2013-10-15'
        self.path = 39
        self.row = 27
        self.year = 2013
        self.sat = 8
        self.max_cloud = 20
        self.root = os.path.join(os.path.dirname(__file__), 'data')

    def test_low_cloud(self):
        g = GoogleDownload(self.start, self.end, self.sat, path=self.path, row=self.row,
                           output_path=self.root, max_cloud_percent=self.max_cloud)
        low, all = g.candidate_scenes(return_list=True)
        print(low, all)

    def test_all_scenes(self):
        g = GoogleDownload(self.start, self.end, self.sat, path=self.path, row=self.row,
                           output_path=self.root, max_cloud_percent=self.max_cloud)
        low, all = g.candidate_scenes(return_list=True)
        print(low, all)


if __name__ == '__main__':
    unittest.main()
# ========================= EOF ====================================================================
