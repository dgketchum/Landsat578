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

import os
import tarfile
import shutil
from warnings import warn
from pandas import read_pickle
from datetime import datetime as dt
from requests import get

try:
    from urllib.parse import urlparse, urlunparse, ParseResult
except ImportError:
    from urlparse import urlparse, urlunparse, ParseResult

from fiona import open as fopen
from shapely.geometry import shape, Point

from update_landsat_metadata import update

SATS = ['LANDSAT_1', 'LANDSAT_2', 'LANDSAT_3', 'LANDSAT_4',
        'LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']
fmt = '%Y-%m-%d'


class BadRequestsResponse(Exception):
    pass


class MissingInitData(Exception):
    pass


class GoogleDownload(object):
    def __init__(self, satellite_number, start_date, end_date,
                 path=None, row=None, latitude=None, longitude=None, max_cloud=70,
                 instrument=None):

        self.sat_num = satellite_number
        self.sat_name = 'LANDSAT_{}'.format(self.sat_num)
        self.instrument = instrument
        self.start = dt.strptime(start_date, fmt)
        self.end = dt.strptime(end_date, fmt)
        self.cloud = max_cloud

        self.p = path
        self.r = row
        self.lat = latitude
        self.lon = longitude
        self._check_pr_lat_lon()

        self.urls = None
        self.scene_ids = None
        self.product_ids = None
        self.scenes_df = None

        self.output = None
        self.current_image = None

        self.scenes_abspath = None
        self.scenes = os.path.abspath(os.path.dirname(__file__).replace('landsat', 'scene_list'))
        self._check_scenes_lists()
        self._get_candidate_scenes()

    def download(self, output_dir, zipped=False,
                 alt_name=None):

        self.output = output_dir
        for ind, row in self.scenes_df.iterrows():
            print('Image {} for {}'.format(row.SCENE_ID, row.DATE_ACQUIRED))
            for band in self.band_map[self.sat_name]:

                url = self._make_url(row, band)

                dst = os.path.join(self.output, row.SCENE_ID, os.path.basename(url))

                out_dir = os.path.join(self.output, row.SCENE_ID)
                if not os.path.isdir(out_dir):
                    os.mkdir(out_dir)

                if not os.path.isfile(dst):
                    self._fetch_image(url, dst)
                else:
                    print('{} exists'.format(dst))

            if zipped:
                tgz_file = '{}.tar.gz'.format(row.SCENE_ID)
                self._zip_image(tgz_file, out_dir)
            if alt_name:
                tgz_file = '{}.tar.gz'.format(alt_name)
                self._zip_image(tgz_file, out_dir)

        return None

    def _check_pr_lat_lon(self):
        if self.p and self.r:
            pass
        elif self.lat and self.lon:
            self._pr_from_latlon()
        else:
            raise MissingInitData(print('Must create GoogleDownload object with both path and row,'
                                        'or with both latitude and longitude'))

    def _check_scenes_lists(self):
        list_dir = [x for x in os.listdir(self.scenes)]
        instruments = ['LANDSAT_1', 'LANDSAT_2', 'LANDSAT_3', 'LANDSAT_4', 'LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']
        for s in instruments:
            if s not in list_dir:
                print('Appears there is not scenes list, downloading and processing...')
                update()
        path = os.path.join(self.scenes, 'LANDSAT_{}'.format(self.sat_num))
        self.scenes_abspath = path

    def _get_candidate_scenes(self):
        df = read_pickle(self.scenes_abspath)
        df = df.loc[(df.CLOUD_COVER < self.cloud) & (df.WRS_PATH == self.p) & (df.WRS_ROW == self.r)
                    & (self.start < df.DATE_ACQUIRED) & (df.DATE_ACQUIRED < self.end)]
        df.dropna(subset=['PRODUCT_ID'], inplace=True, axis=0)
        self.scenes_df = df
        if df.shape[0] == 0:
            warn('There are no images for the satellite, time period, and cloud cover constraints provided.')
        self.urls = df.BASE_URL.values.tolist()
        self.product_ids = df.PRODUCT_ID.values.tolist()
        self.scene_ids = df.SCENE_ID.values.tolist()

    def _pr_from_latlon(self):

        polygons = self._get_path_row_polygons()
        for poly in polygons:
            if Point(self.lon, self.lat).within(poly):
                pass

    def _get_path_row_polygons(self):
        with fopen(self.vectors, 'r') as src:
            polys = []
            for feat in src:
                geo = shape(feat['geometry'])
                polys.append(geo)
        return polys

    @property
    def band_map(self):

        b = {'LANDSAT_1': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_2': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_3': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_4': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],
             'LANDSAT_5': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF', 'B7.TIF', 'MTL.txt'],

             'LANDSAT_7': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF',
                           'B6_VCID_1.TIF', 'B6_VCID_2.TIF', 'B7.TIF', 'B8.TIF', 'MTL.txt'],

             'LANDSAT_8': ['B1.TIF', 'B2.TIF', 'B3.TIF', 'B4.TIF', 'B5.TIF', 'B6.TIF',
                           'B7.TIF', 'B8.TIF', 'B9.TIF', 'B10.TIF', 'B11.TIF', 'BQA.TIF', 'MTL.txt']}
        return b

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

        response = get(url, stream=True)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                print('Getting {}'.format(os.path.basename(url)))
                for chunk in response.iter_content(chunk_size=1024 * 1024 * 8):
                    f.write(chunk)

        elif response.status_code > 399:
            print('Code {}'.format(response.status_code))
            raise BadRequestsResponse(Exception)

    @staticmethod
    def _zip_image(output_filename, source_dir):
        out_location = os.path.dirname(source_dir)
        with tarfile.open(os.path.join(out_location, output_filename), "w:gz") as tar:
            tar.add(source_dir)
        shutil.rmtree(source_dir)


if __name__ == '__main__':
    home = os.path.expanduser('~')
    g = GoogleDownload(8, '2013-07-01', '2013-07-21', path=39, row=27, max_cloud=20)
    out = os.path.join(home, 'landsat_images')
    g.download(out, zipped=False)

# ========================= EOF ================================================================
