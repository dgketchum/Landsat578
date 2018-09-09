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
import gzip
from zipfile import ZipFile
from numpy import unique
from datetime import datetime
from dask.dataframe import read_csv
from requests import get

LANDSAT_METADATA_URL = 'http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz'
SCENES_ZIP = 'index.csv.gz'
SCENES = os.path.join(os.path.dirname(__file__), 'scenes')

WRS_URL = ('https://landsat.usgs.gov/sites/default/files/documents/WRS1_descending.zip',
           'https://landsat.usgs.gov/sites/default/files/documents/WRS2_descending.zip')
WRS_FILES = (os.path.join(os.path.dirname(__file__), 'wrs', 'wrs1_descending.shp'),
             os.path.join(os.path.dirname(__file__), 'wrs', 'wrs2_descending.shp'))
WRS_ZIP = 'wrs.zip'
WRS_DIR = os.path.join(os.path.dirname(__file__), 'wrs')

fmt = '%Y%m%d'
date = datetime.strftime(datetime.now(), fmt)
LATEST = 'scenes_{}'.format(date)

PARSE_DATES = ['DATE_ACQUIRED', 'SENSING_TIME']


def update_metadata_lists():
    print('Please wait while Landsat578 updates Landsat metadata files...')
    if not os.path.isdir(SCENES):
        os.mkdir(SCENES)
    os.chdir(SCENES)
    ls = os.listdir(SCENES)
    for f in ls:
        if 'scenes_' in f and LATEST not in f:
            os.remove(os.path.join(SCENES, f))
    download_latest_metadata()
    split_list()
    os.remove(LATEST)
    os.remove(SCENES_ZIP)
    with open(LATEST, 'w') as empty:
        empty.write('')
    return None


def download_latest_metadata():
    if not os.path.isfile(SCENES_ZIP):
        req = get(LANDSAT_METADATA_URL, stream=True)
        if req.status_code != 200:
            raise ValueError('Bad response {} from request.'.format(req.status_code))

        with open(SCENES_ZIP, 'wb') as f:
            print('Downloading {}'.format(LANDSAT_METADATA_URL))
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    if not os.path.isfile(LATEST):
        with gzip.open(SCENES_ZIP, 'rb') as infile:
            print('unzipping {}'.format(SCENES_ZIP))
            with open(LATEST, 'wb') as outfile:
                for line in infile:
                    outfile.write(line)

    return None


def split_list(_list=LATEST):
    """
    # dtypes = ['object', 'object', 'object', 'object', 'object', 'int64', 'object', 'object',
    #           'object', 'int64', 'int64', 'float64', 'float64', 'float64', 'float64', 'float64',
    #           'int64', 'object']
    #
    # keys = ['SCENE_ID', 'PRODUCT_ID', 'SPACECRAFT_ID', 'SENSOR_ID', 'DATE_ACQUIRED',
    #         'COLLECTION_NUMBER', 'COLLECTION_CATEGORY', 'SENSING_TIME', 'DATA_TYPE', 'WRS_PATH',
    #         'WRS_ROW', 'CLOUD_COVER', 'NORTH_LAT', 'SOUTH_LAT', 'WEST_LON', 'EAST_LON',
    #         'TOTAL_SIZE', 'BASE_URL']
    """
    print('Please wait while scene metadata is split')
    csv = read_csv(_list, dtype={'PRODUCT_ID': object, 'COLLECTION_NUMBER': object,
                                 'COLLECTION_CATEGORY': object}, blocksize=25e6,
                   parse_dates=True)
    csv = csv[csv.COLLECTION_NUMBER != 'PRE']

    sats = unique(csv.SPACECRAFT_ID).tolist()
    for sat in sats:
        print(sat)
        df = csv[csv.SPACECRAFT_ID == sat]
        df.to_parquet('{}'.format(sat))

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
    update_metadata_lists()
# ========================= EOF ================================================================
