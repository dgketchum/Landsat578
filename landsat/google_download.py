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
import re
import sys
import tarfile
import shutil
from lxml import html
from warnings import warn
from pandas import read_pickle, concat, Series
from datetime import datetime as dt
from requests import get

try:
    from urllib.parse import urlparse, urlunparse
except ImportError:
    from urlparse import urlparse, urlunparse

sys.path.append(os.path.dirname(__file__))

from landsat.update_landsat_metadata import update_metadata_lists, get_wrs_shapefiles
from landsat.band_map import BandMap

SATS = ['LANDSAT_1', 'LANDSAT_2', 'LANDSAT_3', 'LANDSAT_4',
        'LANDSAT_5', 'LANDSAT_7', 'LANDSAT_8']

WRS_1 = os.path.join(os.path.dirname(__file__), 'wrs', 'wrs1_descending.shp')
WRS_2 = os.path.join(os.path.dirname(__file__), 'wrs', 'wrs2_descending.shp')
WRS_DIR = os.path.join(os.path.dirname(__file__), 'wrs')

SCENES = os.path.join(os.path.dirname(__file__), 'scenes')

fmt = '%Y-%m-%d'


class BadRequestsResponse(Exception):
    pass


class MissingInitData(Exception):
    pass


class GoogleDownload(object):
    def __init__(self, start, end, satellite, latitude=None, longitude=None,
                 path=None, row=None, max_cloud_percent=70,
                 instrument=None, output_path=None, zipped=False, alt_name=False):

        self.sat_num = satellite
        self.sat_name = 'LANDSAT_{}'.format(self.sat_num)
        self.instrument = instrument
        self.start = dt.strptime(start, fmt)
        self.end = dt.strptime(end, fmt)
        self.cloud = max_cloud_percent

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

        self.urls = None
        self.scene_ids = None
        self.product_ids = None
        self.scenes_df = None
        self.pymetric_ids = None

        self.output = output_path
        self.zipped = zipped
        self.alt_name = alt_name

        self.current_image = None

        self.candidate_scenes()
        self.band_map = BandMap()

    def download(self):

        out_dir = None
        for ind, row in self.scenes_df.iterrows():
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

    def candidate_scenes(self, return_list=False):
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
        self._make_pymetric_ids()
        if return_list:
            return self.scene_ids

    def _check_metadata(self):

        if not os.path.isdir(self.scenes):
            update_metadata_lists()

        path = os.path.join(self.scenes, 'LANDSAT_{}'.format(self.sat_num))
        self.scenes_abspath = path

        if not os.path.isdir(WRS_DIR):
            get_wrs_shapefiles()

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
        conversion_type = 'convert_ll_to_pr'
        base = 'https://landsat.usgs.gov/landsat/lat_long_converter/tools_latlong.php'
        unk_number = 1508518830987

        full_url = '{}?rs={}&rsargs[]={}&rsargs[]={}&rsargs[]=1&rsrnd={}'.format(base, conversion_type,
                                                                                 self.lat, self.lon,
                                                                                 unk_number)
        r = get(full_url)
        tree = html.fromstring(r.text)

        # remember to view source html to build xpath
        # i.e. inspect element > network > find GET with relevant PARAMS
        # > go to GET URL > view source HTML
        p_string = tree.xpath('//table/tr[1]/td[2]/text()')
        self.p = int(re.search(r'\d+', p_string[0]).group())

        r_string = tree.xpath('//table/tr[1]/td[4]/text()')
        self.r = int(re.search(r'\d+', r_string[0]).group())

    def _make_pymetric_ids(self):
        metric_ids = []
        for _id in self.product_ids:
            tag = '{}_{}_{}'.format(_id[:4], _id[10:16], _id[17:25])
            metric_ids.append(tag)
        self.pymetric_ids = metric_ids
        series = Series(data=self.pymetric_ids, name='PYMETRIC_ID', index=self.scenes_df.index)
        self.scenes_df = concat([self.scenes_df, series], axis=1)

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
            tar.add(source_dir)
        shutil.rmtree(source_dir)


if __name__ == '__main__':
    pass

# ========================= EOF ================================================================
