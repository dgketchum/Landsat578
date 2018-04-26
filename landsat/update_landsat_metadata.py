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
import gzip
from numpy import unique
from datetime import datetime
from pandas import read_csv
from requests import get

LANDSAT_METADATA_URL = 'http://storage.googleapis.com/gcp-public-data-landsat/index.csv.gz'
ZIP_PATH = 'index.csv.gz'

SCENES = os.path.dirname(__file__).replace('landsat', 'scenes')

if not os.path.isdir(SCENES):
    os.mkdir(SCENES)
os.chdir(SCENES)
fmt = '%Y%m%d'
date = datetime.strftime(datetime.now(), fmt)
LATEST = 'scenes_{}'.format(date)

PARSE_DATES = ['DATE_ACQUIRED', 'SENSING_TIME']


def update():
    download_latest_metadata()
    split_list()
    return None


def download_latest_metadata():
    if not os.path.isfile(ZIP_PATH):
        req = get(LANDSAT_METADATA_URL, stream=True)
        if req.status_code != 200:
            raise ValueError('Bad response {} from request.'.format(req.status_code))

        with open(ZIP_PATH, 'wb') as f:
            print('Downloading {}'.format(LANDSAT_METADATA_URL))
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    if not os.path.isfile(LATEST):
        with gzip.open(ZIP_PATH, 'rb') as infile:
            print('unzipping {}'.format(ZIP_PATH))
            with open(LATEST, 'wb') as outfile:
                for line in infile:
                    outfile.write(line)

    return None


def split_list(_list=LATEST):
    csv = read_csv(_list, parse_dates=PARSE_DATES)
    sats = unique(csv.SPACECRAFT_ID).tolist()
    for sat in sats:
        df = csv[csv.SPACECRAFT_ID == sat]
        df.to_pickle(sat)

    return None


if __name__ == '__main__':

    update()
# ========================= EOF ================================================================
