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
import re
import requests
from lxml import html
from pandas import DataFrame
from dateutil.rrule import rrule, DAILY
from datetime import datetime, timedelta


class OverpassNotFoundError(Exception):
    pass


class InvalidDateForSatelliteError(Exception):
    pass


class WebSiteOfflineError(Exception):
    pass


def verify_landsat_scene_exists(scene_string):
    if scene_string.startswith('LT5'):
        url_spec = '12266'
    elif scene_string.startswith('LE7'):
        url_spec = '13350'
    elif scene_string.startswith('LC8'):
        url_spec = '13400'
    else:
        raise NotImplementedError('Must choose a valid satellite to find url_spec')

    base = 'https://earthexplorer.usgs.gov/fgdc/'
    url = '{}{}/{}/'.format(base, url_spec, scene_string)

    r = requests.get(url)
    tree = html.fromstring(r.text)
    if r.status_code != 200:
        raise WebSiteOfflineError('USGS application unavailable.')
    string = tree.xpath('//pre/text()')

    split_str = string[0].split('\n')[5].split(':')
    title = [x.strip() for x in split_str]
    if len(title[1]) < 1:
        return False
    else:
        return True


def get_l5_overpass_data(path, row, date):
    if date > datetime(2013, 06, 01):
        raise ValueError('The date requested is after L5 deactivation')

    lat, lon = convert_lat_lon_wrs2pr(path, row, conversion_type='convert_pr_to_ll')

    url = 'https://cloudsgate2.larc.nasa.gov/cgi-bin/predict/predict.cgi'
    # submit form > copy POST data
    # use sat='SATELITE X' with a space
    num_passes = 30
    payload = dict(c='compute', sat='LANDSAT 5', instrument='0-0', res='9', month=str(date.month),
                   day=str(date.day),
                   numday=str(num_passes), viewangle='', solarangle='day', gif='track', ascii='element',
                   lat=str(lat),
                   lon=str(lon), sitename='Optional',
                   choice='track', year=str(date.year))

    r = requests.post(url, data=payload)
    tree = html.fromstring(r.text)
    head_string = tree.xpath('//table/tr[4]/td[1]/pre/b/font/text()')
    col = head_string[0].split()[8]
    ind = []
    zeniths = []

    for row in range(5, num_passes + 5):
        string = tree.xpath('//table/tr[{}]/td[1]/pre/font/text()'.format(row))
        l = string[0].split()
        dt_str = '{}-{}-{} {}:{}'.format(l[0], l[1], l[2], l[3], l[4])
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        ind.append(dt)
        zenith = float(l[8])
        zeniths.append(zenith)
    df = DataFrame(zeniths, index=ind, columns=[col])

    print 'reference dtime overpass: {}'.format(df['zenith'].argmin())
    return df['zenith'].argmin()


def landsat_overpass_time(lndst_path_row, start_date, satellite):

    delta = timedelta(days=20)
    end = start_date + delta

    if satellite == 'LT5':

        if start_date > datetime(2013, 06, 01):
            raise InvalidDateForSatelliteError('The date requested is after L5 deactivation')

        reference_time = get_l5_overpass_data(lndst_path_row[0], lndst_path_row[1], start_date)
        return reference_time

    else:
        if satellite == 'LE7':
            sat_abv = 'L7'
        elif satellite == 'LC8':
            sat_abv = 'L8'

        base = 'https://landsat.usgs.gov/landsat/all_in_one_pending_acquisition/'
        for day in rrule(DAILY, dtstart=start_date, until=end):

            tail = '{}/Pend_Acq/y{}/{}/{}.txt'.format(sat_abv, day.year,
                                                      day.strftime('%b'),
                                                      day.strftime('%b-%d-%Y'))

            url = '{}{}'.format(base, tail)
            r = requests.get(url)

            for line in r.iter_lines():
                l = line.split()
                try:
                    if l[0] == str(lndst_path_row[0]):
                        if l[1] == str(lndst_path_row[1]):
                            # dtime is in GMT
                            time_str = '{}-{}'.format(day.year, l[2])
                            ref_time = datetime.strptime(time_str, '%Y-%j-%H:%M:%S')

                            return ref_time

                except IndexError:
                    pass
                except TypeError:
                    pass

        raise OverpassNotFoundError('Did not find overpass data, check your dates...')


def convert_lat_lon_wrs2pr(lat, lon, conversion_type='convert_ll_to_pr'):
    base = 'https://landsat.usgs.gov/landsat/lat_long_converter/tools_latlong.php'
    unk_number = 1490995492704

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

        print 'path: {}, row: {}'.format(path, row)

        return path, row

    elif conversion_type == 'convert_pr_to_ll':

        full_url = '{}?rs={}&rsargs[]=\n' \
                   '{}&rsargs[]={}&rsargs[]=1&rsrnd={}'.format(base, conversion_type,
                                                               lat, lon, unk_number)

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
