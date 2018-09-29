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
from zipfile import ZipFile

from dask.dataframe import read_csv
from numpy import unique
from requests import get

fmt = '%Y%m%d'
date = datetime.strftime(datetime.now(), fmt)

SENTINEL_METADATA_URL = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/index.csv.gz'
S_SCENES_ZIP = 'l_index.csv.gz'
S_SCENES = os.path.join(os.path.dirname(__file__), 's_scenes')
S_TILES_URL = 'https://sentinel.esa.int/documents/247904/1955685/' \
              'S2A_OPER_GIP_TILPAR_MPC__20151209T095117_V20150622T000000_21000101T000000_B00.kml'
S_TILES_ZIP = 's_tiles.zip'
S_TILES_DIR = os.path.join(os.path.dirname(__file__), 's_tiles')
S_LATEST = 's_scenes_{}'.format(date)

LANDSAT_METADATA_URL = 'http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz'
L_SCENES_ZIP = 's_index.csv.gz'
L_SCENES = os.path.join(os.path.dirname(__file__), 'l_scenes')
WRS_URL = ('https://landsat.usgs.gov/sites/default/files/documents/WRS1_descending.zip',
           'https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip')
WRS_FILES = (os.path.join(os.path.dirname(__file__), 'wrs', 'wrs1_descending.shp'),
             os.path.join(os.path.dirname(__file__), 'wrs', 'wrs2_descending.shp'))
WRS_ZIP = 'wrs.zip'
WRS_DIR = os.path.join(os.path.dirname(__file__), 'wrs')
L_LATEST = 'l_scenes_{}'.format(date)


def update_metadata_lists():
    print('Please wait while Landsat578 updates Landsat metadata files...')
    if not os.path.isdir(L_SCENES):
        os.mkdir(L_SCENES)
    os.chdir(L_SCENES)
    ls = os.listdir(L_SCENES)
    for f in ls:
        if 'l_scenes_' in f and L_LATEST not in f:
            os.remove(os.path.join(L_SCENES, f))
    download_latest_metadata()
    split_list()
    os.remove(L_LATEST)
    os.remove(L_SCENES_ZIP)
    with open(L_LATEST, 'w') as empty:
        empty.write('')

    print('Please wait while Landsat578 updates Sentinel metadata files...')
    if not os.path.isdir(S_SCENES):
        os.mkdir(S_SCENES)
    os.chdir(S_SCENES)
    ls = os.listdir(S_SCENES)
    for f in ls:
        if 's_scenes_' in f and S_LATEST not in f:
            os.remove(os.path.join(S_SCENES, f))
    download_latest_metadata()
    split_list()
    os.remove(S_LATEST)
    os.remove(S_SCENES)
    with open(S_LATEST, 'w') as empty:
        empty.write('')
    return None


def download_latest_metadata():
    if not os.path.isfile(L_SCENES_ZIP):
        req = get(LANDSAT_METADATA_URL, stream=True)
        if req.status_code != 200:
            raise ValueError('Bad response {} from request.'.format(req.status_code))

        with open(L_SCENES_ZIP, 'wb') as f:
            print('Downloading {}'.format(LANDSAT_METADATA_URL))
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    if not os.path.isfile(L_LATEST):
        with gzip.open(L_SCENES_ZIP, 'rb') as infile:
            print('unzipping {}'.format(L_SCENES_ZIP))
            with open(L_LATEST, 'wb') as outfile:
                for line in infile:
                    outfile.write(line)

    if not os.path.isfile(S_SCENES_ZIP):
        req = get(SENTINEL_METADATA_URL, stream=True)
        if req.status_code != 200:
            raise ValueError('Bad response {} from request.'.format(req.status_code))

        with open(S_SCENES_ZIP, 'wb') as f:
            print('Downloading {}'.format(SENTINEL_METADATA_URL))
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    if not os.path.isfile(L_LATEST):
        with gzip.open(S_SCENES_ZIP, 'rb') as infile:
            print('unzipping {}'.format(S_SCENES_ZIP))
            with open(L_LATEST, 'wb') as outfile:
                for line in infile:
                    outfile.write(line)
    return None


def split_list(_list=L_LATEST):
    print('Please wait while scene metadata is split')
    csv = read_csv(_list, dtype={'PRODUCT_ID': object, 'COLLECTION_NUMBER': object,
                                 'COLLECTION_CATEGORY': object}, blocksize=25e6,
                   parse_dates=True)
    csv = csv[csv.COLLECTION_NUMBER != 'PRE']

    sats = unique(csv.SPACECRAFT_ID).tolist()
    for sat in sats:
        print(sat)
        df = csv[csv.SPACECRAFT_ID == sat]
        dst = os.path.join(L_SCENES, sat)
        if os.path.isfile(dst):
            os.remove(dst)
        if not os.path.isdir(dst):
            os.mkdir(dst)
        df.to_parquet('{}'.format(dst))

    return None


def get_wrs_shapefiles():
    if not os.path.isdir(WRS_DIR):
        os.mkdir(WRS_DIR)
    os.chdir(WRS_DIR)
    download_wrs_data()


def download_wrs_data():
    for url, wrs_file in zip(WRS_URL, WRS_FILES):
        if not os.path.isfile(WRS_ZIP):
            req = get(url, stream=True)
            if req.status_code != 200:
                raise ValueError('Bad response {} from request.'.format(req.status_code))

            with open(WRS_ZIP, 'wb') as f:
                print('Downloading {}'.format(url))
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        with ZipFile(WRS_ZIP, 'r') as zip_file:
            print('unzipping {}'.format(WRS_ZIP))
            zip_file.extractall()

        os.remove(WRS_ZIP)

    return None


if __name__ == '__main__':
    pass
# ========================= EOF ================================================================
