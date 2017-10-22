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

from core.usgs_download import get_candidate_scenes_list


class ScenesListTestCase(unittest.TestCase):
    def setUp(self):
        # known overpasses for pr 37, 27
        self.path, self.row = 37, 27
        self.search_start = datetime(2007, 6, 1)
        self.search_end = datetime(2007, 8, 30)
        self.le7_known = ['LE70370272007241EDC00', 'LE70370272007225EDC00',
                          'LE70370272007209EDC00', 'LE70370272007193EDC00',
                          'LE70370272007177EDC00', 'LE70370272007161EDC00']

        self.early_test_path = 43
        self.early_test_row = 33
        self.early_start = datetime(1999, 6, 25)
        self.early_end = datetime(1999, 8, 2)
        self.early_known_l7 = ['LE70430331999213EDC00', 'LE70430331999197EDC00',
                               'LE70430331999181EDC00']

    def test_get_scenes_list(self):
        scenes = get_candidate_scenes_list(path=self.path, row=self.row,
                                           sat_name='LE7',
                                           start_date=self.search_start,
                                           end_date=self.search_end)

        self.assertEqual(scenes, self.le7_known)

    def test_get_scenes_early_l7(self):
        scenes = get_candidate_scenes_list(path=self.early_test_path,
                                           row=self.early_test_row,
                                           sat_name='LE7',
                                           start_date=self.early_start,
                                           end_date=self.early_end)
        self.assertEqual(scenes, self.early_known_l7)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
