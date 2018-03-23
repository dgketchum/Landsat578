# Adapted in part from Olivier Hagolle
# https://github.com/olivierhagolle/LANDSAT-Download
import os
import re
import requests
from future.standard_library import install_aliases
import tarfile
from pandas import read_csv

install_aliases()
from urllib.parse import urlencode
from urllib.request import urlopen, install_opener, build_opener, HTTPCookieProcessor, Request


class StationNotFoundError(Exception):
    pass


class InvalidSatelliteError(Exception):
    pass


class BadRequestsResponse(Exception):
    pass


class InvalidCredentialsResponse(Exception):
    pass


def download_image(url, output_dir, image, creds):
    cookies = HTTPCookieProcessor()
    opener = build_opener(cookies)
    install_opener(opener)

    data = urlopen("https://ers.cr.usgs.gov").read().decode('utf-8')
    m = re.search(r'<input .*?name="csrf_token".*?value="(.*?)"', data)
    if m:
        token = m.group(1)
    else:
        print("Error : CSRF_Token not found")

    params = urlencode(dict(username=creds['account'], password=creds['passwd'], csrf_token=token))
    params = params.encode('ascii')
    request = Request("https://ers.cr.usgs.gov/login", params, headers={})
    f = urlopen(request)

    data = f.read().decode('utf-8')
    f.close()
    if data.find('Invalid username/password') > 0:
        print("Authentification failed")
        raise InvalidCredentialsResponse('Check your credentials, '
                                         'they were rejected by USGS')

    req = urlopen(url)

    uri = req.url
    response = requests.get(uri)

    if response.status_code == 200:
        with open(os.path.join(output_dir, image), 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024 * 8):
                f.write(chunk)

    elif response.status_code > 399:
        print('Code {}'.format(response.status_code))
        raise BadRequestsResponse(Exception)


def unzip_image(tgzfile, outputdir):
    target_tgz = os.path.join(outputdir, tgzfile)
    if os.path.exists(target_tgz):
        print('found tgs: {} \nunzipping...'.format(target_tgz))
        tfile = tarfile.open(target_tgz, 'r:gz')
        tfile.extractall(outputdir)
        print('unzipped\ndeleting tgz: {}'.format(target_tgz))
        os.remove(target_tgz)
    else:
        raise NotImplementedError('Did not find download output directory to unzip...')
    return None


def get_credentials(usgs_path):
    with open(usgs_path) as f:
        (account, passwd) = f.readline().split(' ')
        if passwd.endswith('\n'):
            passwd = passwd[:-1]
        usgs = {'account': account, 'passwd': passwd}
        return usgs


def get_station_list_identifier(product):
    if product.startswith('LC8'):
        identifier = '12864'
        stations = ['LGN']
    elif product.startswith('LE7'):
        identifier = '12267'
        stations = ['EDC', 'SGS', 'AGS', 'ASN', 'SG1', 'CUB', 'COA']
    elif product.startswith('LT5'):
        identifier = '12266'
        stations = ['GLC', 'ASA', 'KIR', 'MOR', 'KHC', 'PAC',
                    'KIS', 'CHM', 'LGS', 'MGR', 'COA', 'MPS', 'CUB']
    else:
        raise NotImplementedError('Must provide valid product string...')

    return identifier, stations


def get_candidate_scenes_list(path, row, sat_name, start_date, end_date, max_cloud_cover=70):
    """
    
    :param path: path (int) 
    :param row: row (int)
    :param sat_name: 'LT5', 'LE7', or 'LC8'
    :param start_date: datetime object start image search
    :param end_date: datetime object finish image search
    :param max_cloud_cover: percent cloud cover according to USGS image metadata, float
    :return: reference overpass = str('YYYYDOY'), station str('XXX') len=3
    """
    sensor_map = {'LT5': 'LANDSAT_TM_C1', 'LE7': 'LANDSAT_ETM_C1', 'LC8': 'LANDSAT_8_C1'}
    sensor = sensor_map[sat_name]
    start = start_date.strftime('%Y-%m-%d')
    end = end_date.strftime('%Y-%m-%d')
    meta_url = 'https://earthexplorer.usgs.gov/EE/InventoryStream/'
    query = 'pathrow?start_path={a}&end_path={a}&start_row={b}&end_row={b}&sensor={c}&' \
            'start_date={d}&end_date={e}&format=CSV'.format(a=path,
                                                            b=row,
                                                            c=sensor,
                                                            d=start,
                                                            e=end)
    url = '{}{}'.format(meta_url, query)
    csv = read_csv(url, header=0)
    csv = csv[csv['cloudCoverFull'] <= max_cloud_cover]
    scene_list = csv['sceneID'].tolist()

    return scene_list


def down_usgs_by_list(scene_list, output_dir, usgs_creds_txt, zipped=False,
                      alt_name=None):
    usgs_creds = get_credentials(usgs_creds_txt)

    for product in scene_list:
        print(product)
        identifier, stations = get_station_list_identifier(product)
        base_url = 'https://earthexplorer.usgs.gov/download/'
        tail_string = '{}/{}/STANDARD/EE'.format(identifier, product)
        url = '{}{}'.format(base_url, tail_string)

        if alt_name:
            tgz_file = '{}.tar.gz'.format(alt_name)
            print('Downloading {} as name {}'.format(product, tgz_file))
        else:

            tgz_file = '{}.tgz'.format(product)

        if not zipped:
            scene_dir = os.path.join(output_dir, product)
            if not os.path.isdir(scene_dir):
                os.mkdir(scene_dir)
            if len(os.listdir(scene_dir)) < 1:
                download_image(url, scene_dir, tgz_file, usgs_creds)
                print('image: {}'.format(os.path.join(scene_dir, tgz_file)))
                if not zipped:
                    unzip_image(tgz_file, scene_dir)
            else:
                print('This image already exists at {}'.format(output_dir))
        else:
            download_image(url, output_dir, tgz_file, usgs_creds)

    return None


if __name__ == '__main__':
    pass

# ===============================================================================
