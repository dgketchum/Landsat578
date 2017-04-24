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
import pkg_resources

from app.landsat_download import create_parser, main


class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

        self.lat = 45.6
        self.lon = -107.5
        self.sat = 'LE7'
        self.path = 36
        self.row = 28
        self.start = '2007-05-01'
        self.end = '2007-05-31'
        self.scene_list = ['LE70360282007122EDC00', 'LE70360282007138EDC00']
        self.scene_list_2 = ['LE70360292007122EDC00', 'LE70360292007138EDC00']

        self.wgs_tile = pkg_resources.resource_filename('data',
                                                        'wrs2_036029_WGS.shp')

    def tearDown(self):
        pass

    def test_empty_args(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_latlon(self):
        print 'Testing valid lat lon...'
        args_list = [self.sat, self.start, self.end, '--return-list',
                     '--lat', str(self.lat), '--lon', str(self.lon)]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.scene_list)

    def test_path_row(self):
        print 'Testing valid path row...'
        args_list = [self.sat, self.start, self.end, '--return-list',
                     '--path', str(self.path), '--row', str(self.row)]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.scene_list)

    def test_shapefile_path_row(self):
        print 'Testing valid shapefile...'
        args_list = [self.sat, self.start, self.end, '--return-list',
                     '--shapefile', self.wgs_tile]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.scene_list_2)


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
