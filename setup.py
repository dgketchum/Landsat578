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

tag = '0.0.1'
name = 'satellite_image'

setup(name='Landsat578',
      version=tag,
      description='Simple API provides a class to process satellite images',
      setup_requires=['nose>=1.0'],
      py_modules=['landsat'],
      license='Apache', classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5'],
      keywords='landsat modis hydrology remote sensing',
      author='David Ketchum',
      author_email='dgketchum at gmail dot com',
      platforms='Posix; MacOS X; Windows',
      packages=['landsat'],
      download_url='https://github.com/{}/{}/archive/{}.tar.gz'.format('dgketchum', name, tag),
      url='https://github.com/dgketchum',
      test_suite='tests.test_suite.suite', install_requires=[],
      entry_points={'console_scripts': ['landsat=landsat:main']}
      )

# ============= EOF ==============================================================
