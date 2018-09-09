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
from __future__ import print_function, absolute_import

import os
import unittest
import shutil
import sys
import pkg_resources

sys.path.append(os.path.dirname(__file__).replace('tests', 'landsat'))

from landsat.landsat_cli import create_parser, main


class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

        self.lat = '45.6'
        self.lon = '-107.5'
        self.sat = '7'
        self.path = '36'
        self.row = '28'
        self.start = '2007-05-01'
        self.end = '2007-05-31'
        self.scene_list = ['LE70360282007122EDC00', 'LE70360282007138EDC00']
        self.scene_list_2 = ['LE70360292007122EDC00', 'LE70360292007138EDC00']

        self.wgs_tile = pkg_resources.resource_filename('tests',
                                                        'data/wrs2_036029_WGS.shp')
        self.config_scenes = ['LT50430302007131PAC01', 'LT50430302007147PAC01']

    def tearDown(self):
        pass

    def test_latlon(self):
        print('Testing valid lat lon...')
        args_list = ['--satellite', self.sat, '--start', self.start, '--end',
                     self.end, '--return-list',
                     '--lat', self.lat, '--lon', self.lon]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.scene_list)

    def test_path_row(self):
        print('Testing valid path row...')
        args_list = ['--satellite', self.sat, '--start', self.start, '--end',
                     self.end, '--return-list',
                     '--path', str(self.path), '--row', str(self.row)]
        args = self.parser.parse_args(args_list)
        scenes = main(args)
        self.assertEqual(scenes, self.scene_list)

    def test_zipped(self):
        print('Testing zipped...')
        root = 'tests'
        base = pkg_resources.resource_filename('tests', 'data/downloader_config.yml')
        filepath = os.path.join(root, base)
        if not os.path.isfile(filepath):
            filepath = base

        temp = os.path.join(os.path.dirname(filepath), 'temp')
        try:
            shutil.rmtree(temp)
        except Exception:
            pass
        os.mkdir(temp)
        args_list = ['--satellite', self.sat, '--start', self.start, '--end',
                     self.end, '--zipped',
                     '--path', str(self.path), '--row', str(self.row), '-o', temp]
        args = self.parser.parse_args(args_list)
        main(args)
        self.assertTrue(os.path.isfile(os.path.join(temp, 'LE70360282007122EDC00.tar.gz')))
        shutil.rmtree(temp)

    # this causes systemexit, use only to make a new config
    # def test_config_no_config_provided(self):
    #     args_list = ['--configuration', os.getcwd()]
    #     args = self.parser.parse_args(args_list)
    #     main(args)
    #     pass

    def test_config(self):
        root = 'tests'
        base = pkg_resources.resource_filename('tests', 'data/downloader_config.yml')
        filepath = os.path.join(root, base)
        if not os.path.isfile(filepath):
            filepath = base

        temp = os.path.join(os.path.dirname(filepath), 'temp')
        try:
            shutil.rmtree(temp)
        except Exception:
            pass
        os.mkdir(temp)

        args_list = ['--configuration', filepath]
        args = self.parser.parse_args(args_list)
        main(args)
        location = os.path.dirname(base)
        self.assertTrue(os.path.isdir(os.path.join(location, 'temp', self.config_scenes[0])))
        self.assertTrue(os.path.isfile(os.path.join(location, 'temp', self.config_scenes[0],
                                                    'LT05_L1TP_043030_20070511_20160908_01_T1_B3.TIF')))
        shutil.rmtree(temp)

    # def test_metadata_creation(self):
    #     wrs = os.path.join(os.path.dirname(__file__).replace('tests', 'landsat'), 'wrs')
    #     scenes = os.path.join(os.path.dirname(__file__).replace('tests', 'landsat'), 'scenes')
    #
    #     try:
    #         shutil.rmtree(wrs)
    #     except:
    #         pass
    #     try:
    #         shutil.rmtree(scenes)
    #     except:
    #         pass
    #
    #     args_list = ['--satellite', self.sat, '--start', self.start, '--end',
    #                  self.end, '--return-list',
    #                  '--path', str(self.path), '--row', str(self.row)]
    #
    #     args = self.parser.parse_args(args_list)
    #     main(args)
    #     self.assertTrue(os.path.isdir(wrs))
    #     self.assertTrue(os.path.isfile(os.path.join(wrs, 'wrs2_descending.shp')))
    #     self.assertTrue(os.path.isdir(scenes))


if __name__ == '__main__':
    unittest.main()

# ===============================================================================
