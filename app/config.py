# ===============================================================================
# Copyright 2017 dgketchum
# Adapted from Jake Ross, https://github.com/jirhiker
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
import sys
import yaml
from datetime import datetime

import paths

DEFAULT_CFG = None
DATETIME_FMT = '%m/%d/%Y'


class RunSpec:
    _obj = None
    winter_start_day = 306

    def __init__(self, obj):
        self._obj = obj
        attrs = ('winter_start_day')

        for attr in attrs:
            setattr(self, attr, self._obj.get(attr))

    @property
    def date_range(self):
        obj = self._obj
        if 'start_year' in obj:
            return (datetime(obj['start_year'],
                             obj['start_month'],
                             obj['start_day']),
                    datetime(obj['end_year'],
                             obj['end_month'],
                             obj['end_day']))

        else:
            return (datetime.strptime(obj['start_date'], DATETIME_FMT),
                    datetime.strptime(obj['end_date'], DATETIME_FMT))


class Config:
    runspecs = None

    def __init__(self, path=None):
        self.load(path=path)

    def load(self, path=None):
        if path is None:
            path = paths.config

        if isinstance(path, (str, unicode)):
            check_config(path)
            rfile = open(path, 'r')
        else:
            rfile = path

        self.runspecs = [RunSpec(doc) for doc in yaml.load_all(rfile)]
        rfile.close()


def check_config(path=None):
    if path is None:
        path = paths.config

    if not os.path.isfile(path):
        print '***** The config file {} does not exist. A default one will be written'.format(path)

        with open(path, 'w') as wfile:
            print '-------------- DEFAULT CONFIG -----------------'
            print DEFAULT_CFG
            print '-----------------------------------------------'
            wfile.write(DEFAULT_CFG)

        print '***** Please edit the config file at {} and rerun the model'.format(path)
        sys.exit()

if __name__ == '__main__':
    pass

# ===============================================================================
