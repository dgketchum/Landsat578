# =============================================================================================
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
# =============================================================================================
from __future__ import print_function, absolute_import

import os
import re
import sys
import tarfile
import shutil
from lxml import html
import numpy as np
from warnings import warn
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from datetime import datetime as dt
from requests import get

try:
    from urllib.parse import urlparse, urlunparse
except ImportError:
    from urlparse import urlparse, urlunparse

sys.path.append(os.path.dirname(__file__))

from landsat.update_landsat_metadata import SatMetaData
from landsat.band_map import BandMap

SATS = ['LANDSAT_1', 'LANDSAT_2', 'LANDSAT_3', 'LANDSAT_4',
        'LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']

WRS_1 = os.path.join(os.path.dirname(__file__), 'wrs', 'WRS1_descending.shp')
WRS_2 = os.path.join(os.path.dirname(__file__), 'wrs', 'WRS2_descending.shp')
WRS_DIR = os.path.join(os.path.dirname(__file__), 'wrs')

SCENES = os.path.join(os.path.dirname(__file__), 'scenes')

fmt = '%Y-%m-%d'


class BadRequestsResponse(Exception):
    pass


class MissingInitData(Exception):
    pass


class GoogleDownload(object):
    def __init__(self, start, end, satellite, latitude=None, longitude=None,
                 path=None, row=None, max_cloud_percent=100,
                 instrument=None, output_path=None, zipped=False, alt_name=False):

        self.sat_num = satellite
        self.sat_name = 'LANDSAT_{}'.format(self.sat_num)
        self.instrument = instrument
        self.start_str = start
        self.end_str = end
        self.start_dt = dt.strptime(start, fmt)
        self.end_dt = dt.strptime(end, fmt)
        self.cloud = float(max_cloud_percent)

        if satellite < 4:
            self.vectors = WRS_1
        else:
            self.vectors = WRS_2

        self.scenes_abspath = None
        self.scenes = SCENES
        self._check_metadata()

        self.p = path
        self.r = row
        self.lat = latitude
        self.lon = longitude
        self._check_pr_lat_lon()

        self.urls_low_cloud = None
        self.product_ids_low_cloud = None
        self.scene_ids_low_cloud = None
        self.scenes_low_cloud = None

        self.urls_all = None
        self.product_ids_all = None
        self.scene_ids_all = None
        self.scenes_all = None

        self.selected_scenes = None
        self.pymetric_ids = None

        self.output = output_path
        self.zipped = zipped
        self.alt_name = alt_name

        self.current_image = None

        self.candidate_scenes()
        self.band_map = BandMap()

    def download(self, list_type='low_cloud'):

        if list_type == 'low_cloud':
            scenes = self.scenes_low_cloud
        elif list_type == 'all':
            scenes = self.scenes_all
        elif list_type == 'selected':
            scenes = self.selected_scenes

        out_dir = None
        for ind, row in scenes.iterrows():
            print('Image {} for {}'.format(row.SCENE_ID, row.DATE_ACQUIRED))
            for band in self.band_map.file_suffixes[self.sat_name]:

                url = self._make_url(row, band)

                dst = os.path.join(self.output, row.SCENE_ID, os.path.basename(url))

                out_dir = os.path.join(self.output, row.SCENE_ID)
                if not os.path.isdir(out_dir):
                    os.mkdir(out_dir)

                if not os.path.isfile(dst):
                    self._fetch_image(url, dst)

            if self.zipped:
                tgz_file = '{}.tar.gz'.format(row.SCENE_ID)
                self._zip_image(tgz_file, out_dir)

            if self.alt_name:
                tgz_file = '{}.tar.gz'.format(row.PYMETRIC_ID)
                self._zip_image(tgz_file, out_dir)

        return None

    def candidate_scenes(self, return_list=False, list_type='low_cloud'):

        filters = None
        path = self.scenes_abspath

        if isinstance(self.p, int):
            filters = [[('WRS_PATH', '=', self.p), ('WRS_ROW', '=', self.r)]]
        elif isinstance(self.p, list):
            filters = [[('WRS_PATH', 'in', self.p), ('WRS_ROW', 'in', self.r)]]

        df = pd.read_parquet(path, engine="pyarrow", filters=filters)

        s, e = pd.Timestamp(self.start_dt), pd.Timestamp(self.end_dt)

        df['DATE_ACQUIRED'] = df['DATE_ACQUIRED'].apply(pd.to_datetime)
        df = df.loc[(s < df.DATE_ACQUIRED) & (df.DATE_ACQUIRED < e)]

        cloud_select = df.loc[(df.CLOUD_COVER < self.cloud)]
        cloud_select.dropna(subset=['PRODUCT_ID'], inplace=True, axis=0)

        self.scenes_all = df
        self.scenes_low_cloud = cloud_select
        if cloud_select.shape[0] == 0 or df.shape[0] == 0:
            warn('There are no images for the satellite, time period, '
                 'and cloud cover constraints provided.')

        self.urls_low_cloud = df.BASE_URL.values.tolist()
        self.product_ids_low_cloud = df.PRODUCT_ID.values.tolist()
        self.scene_ids_low_cloud = df.SCENE_ID.values.tolist()

        self.urls_all = cloud_select.BASE_URL.values.tolist()
        self.product_ids_all = cloud_select.PRODUCT_ID.values.tolist()
        self.scene_ids_all = cloud_select.SCENE_ID.values.tolist()

        if return_list:
            if list_type == 'low_cloud':
                return self.scene_ids_low_cloud

            elif list_type == 'all':
                return self.scene_ids_all

            else:
                raise AttributeError('Must choose list return type all or low_cloud')
        else:
            return None

    def select_scenes(self, n):
        scn = self.scenes_all
        s = scn.sort_values(by='SENSING_TIME').index.values.tolist()
        c = scn.sort_values(by='SENSING_TIME')['CLOUD_COVER'].values.tolist()
        ls = self._split_list(s, n)
        lc = self._split_list(c, n)
        c_idx = [c.index(min(c)) for c in lc]
        select = [l[i] for l, i in zip(ls, c_idx)]
        self.selected_scenes = scn.loc[select]
        pass

    def _check_metadata(self):

        if not os.path.isdir(self.scenes):
            SatMetaData(sat='landsat').update_metadata_lists()

        path = os.path.join(self.scenes, 'LANDSAT_{}'.format(self.sat_num))
        if not os.path.isdir(path):
            SatMetaData(sat='landsat').update_metadata_lists()
        self.scenes_abspath = path

        if not os.path.isdir(WRS_DIR):
            SatMetaData(sat='landsat').get_wrs_shapefiles()

    def _check_pr_lat_lon(self):
        if self.p and self.r:
            try:
                self.p, self.r = int(self.p), int(self.r)
            except TypeError:
                pass
        elif self.lat and self.lon:
            self._get_path_row()
        else:
            raise MissingInitData(print('Must create GoogleDownload object with both path and row,'
                                        'or with both latitude and longitude'))

    def _get_path_row(self):
        """
        :param lat: Latitude float
        :param lon: Longitude float
                'convert_pr_to_ll' [path, row to coordinates]
        :return: lat, lon tuple or path, row tuple
        """
        if self.sat_num > 3:
            shp = WRS_2
        else:
            shp = WRS_1

        wrs = gpd.read_file(shp)
        pt = Point(self.lon, self.lat)
        inter = wrs[wrs.intersects(pt)]
        inter = inter[['PATH', 'ROW', 'PR_', 'WRSPR']]
        if inter.shape[0] == 0:
            raise NotImplementedError('Lat/Lon point failed to intersect the worldwide WRS, check the numbers')
        elif inter.shape[0] == 1:
            self.p, self.r = inter.iloc[0, 'PATH'], inter.iloc[0, 'ROW']
        else:
            self.path_rows = [pr for pr in inter['WRSPR']]
            self.p, self.r = [pr for pr in inter['PATH']], [pr for pr in inter['ROW']]
            print('Lat/Lon produced multiple path/row intersects: {}'.format(self.path_rows))

    @staticmethod
    def _make_url(row, band):

        parse = urlparse('http://storage.googleapis.com/gcp-public-data-landsat/LC08/01/037/029/'
                         'LC08_L1TP_037029_20130602_20170310_01_T1/LC08_L1TP_037029_20130602_20170310_01_T1_B2.TIF')

        base = row.BASE_URL.replace('gs://', '')
        path = '{}/{}_{}'.format(base, row.PRODUCT_ID, band)
        url = urlunparse([parse.scheme, parse.netloc, path, '', '', ''])
        return url

    @staticmethod
    def _fetch_image(url, destination_path=None):

        if not destination_path:
            destination_path = os.path.join(os.getcwd(), os.path.basename(url))

        try:
            response = get(url, stream=True)
            if response.status_code == 200:
                with open(destination_path, 'wb') as f:
                    print('Getting {}'.format(os.path.basename(url)))
                    for chunk in response.iter_content(chunk_size=1024 * 1024 * 8):
                        f.write(chunk)

            elif response.status_code > 399:
                print('Code {} on {}'.format(response.status_code, url))
                raise BadRequestsResponse(Exception)
        except BadRequestsResponse:
            pass

    @staticmethod
    def _zip_image(output_filename, source_dir):
        out_location = os.path.dirname(source_dir)
        with tarfile.open(os.path.join(out_location, output_filename), "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        shutil.rmtree(source_dir)

    @staticmethod
    def _split_list(seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out


if __name__ == '__main__':
    pass

# ========================= EOF ================================================================
