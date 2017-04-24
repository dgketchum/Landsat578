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

from setuptools import setup

os.environ['TRAVIS_CI'] = 'True'

setup(name='Landsat578',
      version='0.1',
      setup_requires=['nose>=1.0'],
      py_modules=['landsat'],
      url='https://github.com/dgketchum/Landsat578',
      author='David Ketchum',
      author_email='dgketchum@gmail.com',
      packages=['landsat',
                'tests',
                'app',
                'data'],
      test_suite='tests.test_suite.suite', install_requires=['gdal', 'osr'])

# ============= EOF =============================================
