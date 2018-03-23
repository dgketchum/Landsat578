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
import re
import requests
from lxml import html


class OverpassNotFoundError(Exception):
    pass


class InvalidDateForSatelliteError(Exception):
    pass


class WebSiteOfflineError(Exception):
    pass


def convert_lat_lon_wrs2pr(lat, lon, conversion_type='convert_ll_to_pr'):
    """ 
    :param lat: Latitude float
    :param lon: Longitude float
    :param conversion_type: 'convert_ll_to_pr' [coordinates to path, row]; 
            'convert_pr_to_ll' [path, row to coordinates]
    :return: lat, lon tuple or path, row tuple
    """
    base = 'https://landsat.usgs.gov/landsat/lat_long_converter/tools_latlong.php'
    # I never figured out how to get unk_number programatically, and it changes,
    # unknown parameter purpose
    unk_number = 1508518830987

    if conversion_type == 'convert_ll_to_pr':

        full_url = '{}?rs={}&rsargs[]={}&rsargs[]={}&rsargs[]=1&rsrnd={}'.format(base, conversion_type,
                                                                                 lat, lon,
                                                                                 unk_number)
        r = requests.get(full_url)
        tree = html.fromstring(r.text)

        # remember to view source html to build xpath
        # i.e. inspect element > network > find GET with relevant PARAMS
        # > go to GET URL > view source HTML
        p_string = tree.xpath('//table/tr[1]/td[2]/text()')
        path = int(re.search(r'\d+', p_string[0]).group())

        r_string = tree.xpath('//table/tr[1]/td[4]/text()')
        row = int(re.search(r'\d+', r_string[0]).group())

        print('path: {}, row: {}'.format(path, row))

        return path, row
    elif conversion_type == 'convert_pr_to_ll':

        full_url = '{}?rs={}&rsargs[]=\n' \
                   '{}&rsargs[]={}&rsargs[]=1&rsrnd={}'.format(base, conversion_type,
                                                               lat, lon, unk_number)
        # this needs to depend on something other than USGS
        r = requests.get(full_url)
        tree = html.fromstring(r.text)

        lat_string = tree.xpath('//table/tr[2]/td[2]/text()')
        lat = float(re.search(r'[+-]?\d+(?:\.\d+)?', lat_string[0]).group())

        lon_string = tree.xpath('//table/tr[2]/td[4]/text()')
        lon = float(re.search(r'[+-]?\d+(?:\.\d+)?', lon_string[0]).group())

        return lat, lon

    else:
        raise NotImplementedError('Must chose either convert_pr_to_ll or convert_ll_to_pr')


if __name__ == '__main__':
    pass

# ==================================================================================
