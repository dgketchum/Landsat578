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
from tempfile import mkdtemp
import ogr
import shutil

from landsat import vector_tools


class VectorTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_foler = mkdtemp()
        self.out_shp_str = os.path.join(self.temp_foler, 'out_shape_str.shp')
        self.out_pts = os.path.join(self.temp_foler, 'out_points.shp')
        self.lat = 46.99
        self.lon = -109.61
        self.poly_interior_points = [(-110.4, 48.3), (-108.1, 47.9), (-108.7, 46.6),
                                     (-110.8, 46.9)]
        self.tup = (38, 27)
        self.lst = [(38, 27)]
        self.target_tile_pts = [(488245.30243298115, 292668.1008154524), (488238.7897641528, 292669.6144005801),
                                (488416.7260886859, 293328.3133520024), (490445.02364716836, 300846.8477201403),
                                (529685.3760580911, 450127.9607610224), (531409.2720712859, 456862.50326944795),
                                (531788.1465979685, 458344.7094121693), (531803.6518557359, 458341.1182646604),
                                (712217.0961924061, 419630.0785964296), (711273.0359873119, 415925.9308217316),
                                (670521.1234916867, 260742.92484704658), (668624.2008179231, 253730.22862013045),
                                (488245.30243298115, 292668.1008154524)]
        self.field_attrs = {'1': {'PATH': 38, 'ROW': 27, 'LON': self.lon, 'LAT': self.lat}}
        self.test_shapefile = os.path.join(self.temp_foler, 'test_shape.shp')
        vector_tools.points_to_shapefile(self.field_attrs, self.test_shapefile)
        self.overlap_tile_pts = [(291624.54666122684, 605949.2015429772), (291625.9314961701, 605942.6602871811),
                                 (292288.0119187373, 606107.5698328196), (299845.08975377394, 607987.177405117),
                                 (449871.13801362034, 644275.4787099798), (456638.3724945902, 645866.2073925897),
                                 (458127.76320690656, 646215.7732126429), (458124.478583372, 646231.3462857858),
                                 (422979.4404748881, 827373.2293111344), (419257.39266950724, 826502.4132903113),
                                 (263300.78563174425, 788819.2547621517), (256252.03876927294, 787061.0193768718),
                                 (291624.54666122684, 605949.2015429772)]

    def tearDown(self):
        os.remove(self.test_shapefile)
        shutil.rmtree(self.temp_foler)

    def test_point(self):
        # test with AmeriFlux US-MJ-1
        point = vector_tools.lat_lon_to_ogr_point(self.lat, self.lon)
        self.assertTrue(type(point), ogr.Geometry)

    def test_pt_to_poly_geo(self):
        poly = vector_tools.points_to_ogr_polygon(self.target_tile_pts)
        self.assertTrue(type(poly), ogr.Geometry)

    def test_pt_to_shp(self):
        vector_tools.points_to_shapefile(self.field_attrs, self.out_pts)
        self.assertTrue(ogr.Open(self.out_pts), ogr.DataSource)
        os.remove(self.out_pts)

    def test_poly_to_shp(self):
        poly = vector_tools.points_to_ogr_polygon(self.target_tile_pts)
        vector_tools.poly_to_shp(poly, self.out_shp_str, self.field_attrs)
        dct = vector_tools.shp_to_attr_dict(self.out_shp_str)
        self.assertTrue(ogr.Open(self.out_shp_str), ogr.DataSource)
        self.assertEqual(self.field_attrs, dct)
        os.remove(self.out_shp_str)

    def test_shp_to_feat(self):
        feat = vector_tools.shp_to_ogr_features(self.test_shapefile)
        self.assertTrue(type(feat), ogr.Feature)

    def test_shp_to_geom(self):
        geo = vector_tools.shp_to_ogr_geometries(self.test_shapefile)
        self.assertTrue(type(geo[0]), ogr.Geometry)
        self.assertTrue(type(geo), list)

    def test_pathrow_from_field(self):
        path_list = vector_tools.get_pr_from_field(self.test_shapefile)
        self.assertTrue(type(path_list), list)
        self.assertTrue(type(path_list[0]), tuple)
        for item in path_list:
            self.assertEqual(len(str(item[0])), 3)
            self.assertEqual(len(str(item[1])), 3)

    def test_point_multipath(self):
        tup_result = vector_tools.get_pr_multipath((self.lon, self.lat), self.test_shapefile)
        lst_result = vector_tools.get_pr_multipath([(self.lon, self.lat)], self.test_shapefile)
        vector_tools.points_to_shapefile(self.field_attrs, self.out_pts)
        points_shp_result = vector_tools.get_pr_multipath(self.out_pts, self.test_shapefile)
        print tup_result, lst_result, points_shp_result
        self.assertEqual(tup_result, lst_result)
        self.assertEqual(lst_result, points_shp_result)

if __name__ == '__main__':
    unittest.main()

# ===============================================================================
