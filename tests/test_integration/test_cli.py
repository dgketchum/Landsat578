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

import pkg_resources

from landsat.landsat import create_parser, main
from landsat.landsat import TooFewInputsError


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

        self.wgs_tile = pkg_resources.resource_filename('tests',
                                                        'data/wrs2_036029_WGS.shp')
        self.config_scenes = ['LT50430302007147PAC01', 'LT50430302007131PAC01']

    def tearDown(self):
        pass

    def test_empty_args(self):
        with self.assertRaises(TooFewInputsError):
            args = self.parser.parse_args([])
            scenes = main(args)

    def test_latlon(self):
        print('Testing valid lat lon...')
        args_list = ['--satellite', self.sat, '--start', self.start, '--end',
                     self.end, '--return-list',
                     '--lat', str(self.lat), '--lon', str(self.lon)]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        scenes.reverse()
        self.assertEqual(scenes, self.scene_list)

    def test_path_row(self):
        print('Testing valid path row...')
        args_list = ['--satellite', self.sat, '--start', self.start, '--end',
                     self.end, '--return-list',
                     '--path', str(self.path), '--row', str(self.row)]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        scenes.reverse()
        self.assertEqual(scenes, self.scene_list)

    # this cause systemexit, use only to make your own config
    # def test_config_no_config_provided(self):
    #     dirname = 'data'
    #     if __name__ == '__main__':
    #         dirname = 'tests/data'
    #     args_list = ['--configuration', dirname]
    #     args = self.parser.parse_args(args_list)
    #     main(args)
    #     pass

    def test_config(self):
        # test suite needs handler to remove test-level dir
        root = 'tests'
        base = os.path.join('data', 'test_downloader_config.yml')
        filepath = os.path.join(root, base)
        if not os.path.isfile(filepath):
            filepath = base

        args_list = ['--configuration', filepath]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.config_scenes)

    def test_pymetric_config(self):
        # test suite needs handler to remove test-level dir
        root = 'tests'
        base = os.path.join('data', 'test_downloader_pymetric_config.yml')
        filepath = os.path.join(root, base)
        if not os.path.isfile(filepath):
            filepath = base

        args_list = ['--configuration', filepath]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.config_scenes)

if __name__ == '__main__':
    unittest.main()

# ===============================================================================
