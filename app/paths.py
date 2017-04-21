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

from datetime import datetime


class PathsNotSetExecption(BaseException):
    def __str__(self):
        return 'paths.build(in_root, out_root) needs to be called before the model will run.'


class Paths:

    polygons = None

    def __init__(self):
        self._is_set = False
        self.config = os.path.join(os.path.expanduser('~'), 'ETRM_CONFIG.yml')

    def input_path(self, path):
        return os.path.join(self.etrm_input_root, path)

    def set_polygons_path(self, p):
        self.polygons = self.input_path(p)

    def verify(self):
        attrs = ('etrm_input_root',
                 'etrm_output_root')

        nonfound = []

        for attr in attrs:
            v = getattr(self, attr)
            if not os.path.exists(v):
                print 'NOT FOUND {}: {}'.format(attr, v)
                nonfound.append((attr, v))

        if nonfound:
            sys.exit(1)

    def is_set(self):
        return self._is_set

paths = Paths()

# ===============================================================================
