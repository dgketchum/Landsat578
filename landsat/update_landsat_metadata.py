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

import gzip
import os
from datetime import datetime
from zipfile import ZipFile, BadZipFile
from fastkml import kml

from dask.dataframe import read_csv
from numpy import unique
from requests import get

fmt = '%Y%m%d'
date = datetime.strftime(datetime.now(), fmt)


class SatMetaData(object):
    """ ... """

    def __init__(self, sat):

        if sat == 'landsat':
            self.sat = 'landsat'
            self.scenes_zip = 'l_index.csv.gz'
            self.metadata_url = 'http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz'
            self.vector_url = ['https://landsat.usgs.gov/sites/default/files/documents/WRS1_descending.zip',
                               'https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip']
            self.vector_files = (os.path.join(os.path.dirname(__file__), 'wrs', 'wrs1_descending.shp'),
                                 os.path.join(os.path.dirname(__file__), 'wrs', 'wrs2_descending.shp'))
            self.vector_zip = 'wrs.zip'
            self.vector_dir = os.path.join(os.path.dirname(__file__), 'wrs')
            self.scenes = os.path.join(os.path.dirname(__file__), 'l_scenes')
            self.latest = 'l_scenes_{}'.format(date)

        elif sat == 'sentinel':
            self.sat = 'sentinel'
            self.metadata_url = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz'
            self.scenes_zip = 's_index.csv.gz'
            self.scenes = os.path.join(os.path.dirname(__file__), 's_scenes')
            # a = 'https://sentinel.esa.int/documents/247904/1955685/'
            # b = 'S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml'
            # self.vector_url = ['{}{}'.format(a, b)]
            self.vector_url = 'http://earth-info.nga.mil/GandG/coordsys/zip/MGRS/MGRS_100kmSQ_ID/MGRS_100kmSQ_ID.zip'
            self.vector_files = [os.path.join(os.path.dirname(__file__), 's_tiles', 'tiles.shp')]
            self.vector_zip = 's_tiles.kml'
            self.vector_dir = os.path.join(os.path.dirname(__file__), 's_tiles')
            self.latest = 's_scenes_{}'.format(date)

        else:
            raise NotImplementedError('must choose from "sentinel" or "landsat"')

    def update_metadata_lists(self):
        print('Please wait while Landsat578 updates {} metadata files...'.format(self.sat))
        if not os.path.isdir(self.scenes):
            os.mkdir(self.scenes)
        os.chdir(self.scenes)
        ls = os.listdir(self.scenes)
        for f in ls:
            if 'l_scenes_' in f and self.latest not in f:
                os.remove(os.path.join(self.scenes, f))
        self.download_latest_metadata()
        self.split_list()
        self.get_wrs_shapefiles()
        os.remove(self.latest)
        os.remove(self.scenes_zip)
        with open(self.latest, 'w') as empty:
            empty.write('')
        return None

    def download_latest_metadata(self):

        if not os.path.isfile(self.latest):
            req = get(self.metadata_url, stream=True)
            if req.status_code != 200:
                raise ValueError('Bad response {} from request.'.format(req.status_code))

            with open(self.scenes_zip, 'wb') as f:
                print('Downloading {}'.format(self.metadata_url))
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            print('you have the latest {} metadata'.format(self.sat))

        if not os.path.isfile(self.latest):
            with gzip.open(self.scenes_zip, 'rb') as infile:
                print('unzipping {}'.format(self.scenes_zip))
                with open(self.latest, 'wb') as outfile:
                    for line in infile:
                        outfile.write(line)

        return None

    def split_list(self):
        if self.sat == 'landsat':
            print('Please wait while {} scene metadata is split'.format(self.sat))
            csv = read_csv(self.latest, dtype={'PRODUCT_ID': object, 'COLLECTION_NUMBER': object,
                                               'COLLECTION_CATEGORY': object}, blocksize=25e6,
                           parse_dates=True)
            csv = csv[csv.COLLECTION_NUMBER != 'PRE']

            sats = unique(csv.SPACECRAFT_ID).tolist()
            for sat in sats:
                print(sat)
                df = csv[csv.SPACECRAFT_ID == sat]
                dst = os.path.join(self.latest, sat)
                if os.path.isfile(dst):
                    os.remove(dst)
                if not os.path.isdir(dst):
                    os.mkdir(dst)
                df.to_parquet('{}'.format(dst))
        else:
            dst = os.path.join(self.scenes, self.sat)
            if os.path.isfile(dst):
                os.remove(dst)
            if not os.path.isdir(dst):
                os.mkdir(dst)
            df = read_csv(self.latest)
            df.to_parquet('{}'.format(dst))

        return None

    def get_wrs_shapefiles(self):
        if not os.path.isdir(self.vector_dir):
            os.mkdir(self.vector_dir)
        os.chdir(self.vector_dir)
        self.download_wrs_data()

    def download_wrs_data(self):
        for url, wrs_file in zip(self.vector_url, self.vector_files):
            if not os.path.isfile(wrs_file):
                req = get(url, stream=True)
                if req.status_code != 200:
                    raise ValueError('Bad response {} from request.'.format(req.status_code))

                with open(self.vector_zip, 'wb') as f:
                    print('Downloading {}'.format(url))
                    for chunk in req.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            try:
                with ZipFile(self.vector_zip, 'r') as zip_file:
                    print('unzipping {}'.format(self.vector_zip))
                    zip_file.extractall()

            except BadZipFile:
                with open(self.vector_zip) as doc:
                    s = doc.read()
                    k = kml.KML()
                    k.from_string(s)
                    features = list(k.features())
                for f in features:
                    pass
            os.remove(self.vector_zip)

        return None


if __name__ == '__main__':
    m = SatMetaData(sat='sentinel')
    m.update_metadata_lists()
# ========================= EOF ================================================================
