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
import shutil
from datetime import datetime

from core import download_composer as dc


class ScenesDownerTestCaseL7Early(unittest.TestCase):
    def setUp(self):
        # known overpasses for pr 37, 27
        self.path, self.row = 37, 27
        self.search_start = datetime(1999, 6, 1)
        self.search_end = datetime(1999, 7, 30)
        self.le7_known = ['LE70370271999187EDC00']
        self.home = os.path.expanduser('~')
        self.output = os.path.join(self.home, 'images', 'sandbox', 'downer')
        self.usgs_creds = os.path.join(self.home, 'images', 'usgs.txt')

    def test_down_scenes_list(self):
        scenes = dc.download_landsat(path=self.path, row=self.row,
                                     satellite='LE7',
                                     output_path=self.output,
                                     start=self.search_start,
                                     usgs_creds=self.usgs_creds,
                                     end=self.search_end, max_cloud=100)

        sub_folder = os.path.join(self.output, 'LE7_37_27', 'LE70370271999187EDC00')
        files = os.listdir(sub_folder)
        known = ['LE07_L1TP_037027_19990706_20161003_01_T1_ANG.txt',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B1.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B2.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B3.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B4.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B5.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B6_VCID_1.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B6_VCID_2.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B7.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_B8.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_BQA.TIF',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_GCP.txt',
                 'LE07_L1TP_037027_19990706_20161003_01_T1_MTL.txt',
                 'README.GTF']
        self.assertEqual(files, known)
        shutil.rmtree(sub_folder)


class NevadaDownloadTestCase(unittest.TestCase):
    def setUp(self):
        # known overpasses for pr 43, 30
        self.path, self.row = 43, 30
        self.search_start = datetime(2015, 6, 15)
        self.search_end = datetime(2015, 6, 27)
        self.le7_known = ['LE70430302015177EDC00']
        self.home = os.path.expanduser('~')
        self.output = os.path.join(self.home, 'images', 'sandbox', 'downer')
        self.usgs_creds = os.path.join(self.home, 'images', 'usgs.txt')
        self.known_scene = ['LE70430302015177EDC00']
        self.search_start = datetime(2015, 6, 15)
        self.search_end = datetime(2015, 6, 27)

    def test_downloader(self):
        dc.download_landsat(start=self.search_start, end=self.search_end,
                            satellite='LE7', output_path=self.output,
                            usgs_creds=self.usgs_creds,
                            path=self.path, row=self.row,
                            return_list=False)

        sub_folder = os.path.join(self.output, 'LE7_43_30', 'LE70430302015177EDC00')
        files = os.listdir(sub_folder)
        known = ['gap_mask',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_ANG.txt',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B1.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B2.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B3.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B4.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B5.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B6_VCID_1.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B6_VCID_2.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B7.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_B8.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_BQA.TIF',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_GCP.txt',
                 'LE07_L1TP_043030_20150626_20160902_01_T1_MTL.txt',
                 'README.GTF']
        self.assertEqual(files, known)
        shutil.rmtree(sub_folder)


class DownloadTestCase(unittest.TestCase):
    def setUp(self):
        self.home = os.path.expanduser('~')
        self.start = datetime(2007, 5, 1)
        self.end = datetime(2007, 5, 30)
        self.sat = 'LT5'
        self.output = os.path.join(self.home, 'images', 'sandbox', 'downer')
        self.usgs_creds = os.path.join(self.home, 'images', 'usgs.txt')
        self.path, self.row = 37, 27
        self.known_scene = ['LT50370272007137PAC01', 'LT50370272007121PAC01']

    def tearDown(self):
        pass

    def test_scene_list(self):
        scene_list = dc.download_landsat(self.start, self.end, self.sat,
                                         path=self.path, row=self.row,
                                         return_list=True)
        self.assertEqual(self.known_scene, scene_list)

        # can't run the download test on travis.

    def test_downloader(self):
        dc.download_landsat(start=self.start, end=self.end,
                            satellite=self.sat, output_path=self.output,
                            usgs_creds=self.usgs_creds,
                            path=self.path, row=self.row,
                            return_list=False)
        sub_folder = os.path.join(self.output, 'LT5_37_27', 'LT50370272007121PAC01')
        files = os.listdir(sub_folder)
        known = ['LT05_L1TP_037027_20070501_20160910_01_T1_ANG.txt',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B1.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B2.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B3.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B4.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B5.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B6.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_B7.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_BQA.TIF',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_GCP.txt',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_MTL.txt',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_VER.jpg',
                 'LT05_L1TP_037027_20070501_20160910_01_T1_VER.txt',
                 'README.GTF']
        self.assertEqual(files, known)
        shutil.rmtree(sub_folder)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
