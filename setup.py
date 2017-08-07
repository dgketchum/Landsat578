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

try:
    from setuptools import setup

    setup_kwargs = {'entry_points': {'console_scripts': ['landsat=landsat.landsat:__main__']}}
except ImportError:
    from distutils.core import setup

    setup_kwargs = {'scripts': ['bin/landsat']}

tag = '0.3.77'

setup(name='Landsat578',
      version=tag,
      description='Very simple API to download Landsat data from LT5, LE7, and LC8 from USGS',
      setup_requires=['nose>=1.0'],
      py_modules=['landsat'],
      license='Apache', classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7'],
      keywords='landsat download hydrology remote sensing',
      author='David Ketchum',
      author_email='dgketchum@gmail.com',
      platforms='Posix; MacOS X; Windows',
      packages=['landsat'],
      download_url='https://github.com/{}/{}/archive/{}.tar.gz'.format('dgketchum', 'Landsat578', tag),
      url='https://github.com/dgketchum',
      test_suite='tests.test_suite.suite', install_requires=['lxml==3.7.3', 'numpy==1.12.1', 'pandas==0.19.2',
                                                             'python-dateutil==2.6.0', 'pytz==2017.2',
                                                             'requests==2.13.0', 'six==1.10.0'],
      **setup_kwargs)

# ============= EOF ==============================================================
