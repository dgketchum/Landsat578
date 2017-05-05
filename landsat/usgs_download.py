# Adapted in part from Olivier Hagolle
# https://github.com/olivierhagolle/LANDSAT-Download
import os

import tarfile
import requests
from usgs import api, USGS_API, payloads, USGSError
from datetime import datetime, timedelta

import web_tools


class StationNotFoundError(Exception):
    pass


class InvalidSatelliteError(Exception):
    pass


class NotaTGZError(Exception):
    pass


def download_chunks(sat, product, out_dir, usgs_creds):

    node = 'EE'

    if sat == 'LT5':
        dataset = 'LANDSAT_TM_C1'
    elif sat == 'LE7':
        dataset = 'LANDSAT_ETM'
    elif sat == 'LC8':
        dataset = 'LANDSAT_8_C1'
    else:
        raise InvalidSatelliteError

    login_url = '{}/login'.format(USGS_API)

    payload = {"jsonRequest": payloads.login(usgs_creds['username'],
                                             usgs_creds['password'])}


    post_response = login_post.json()
    api_key = post_response['data']

    meta_url = '{}/metadata'.format(USGS_API)

    payload = {
        "jsonRequest": payloads.metadata(dataset, node, entityids, api_key=api_key)
    }
    r = requests.post(meta_url, payload)
    response = r.json()

    url = '{}/download'.format(USGS_API)

    payload = {"jsonRequest": payloads.download(dataset, node, product,
                                                'STANDARD', api_key=api_key)}
    down_post = s.post(url, payload)

    print down_post


def unzip_image(tgzfile, outputdir):
    target_tgz = os.path.join(outputdir, tgzfile)
    print 'target tgz: {}'.format(target_tgz)
    if os.path.exists(target_tgz):
        tfile = tarfile.open(target_tgz, 'r:gz')
        tfile.extractall(outputdir)
        print 'unzipped\ndeleting tgz: {}'.format(target_tgz)
        os.remove(target_tgz)
    else:
        raise NotImplementedError('Did not find download output directory to unzip: {}'.format(target_tgz))
    return None


def get_credentials(usgs_path):
    with file(usgs_path) as f:
        (account, passwd) = f.readline().split(' ')
        if passwd.endswith('\n'):
            passwd = passwd[:-1]
        usgs = {'username': account, 'password': passwd}
        return usgs


def get_station_list_identifier(product):
    if product.startswith('LC8'):
        identifier = '4923'
        stations = ['LGN']
    elif product.startswith('LE7'):
        identifier = '3373'
        stations = ['EDC', 'SGS', 'AGS', 'ASN', 'SG1', 'CUB', 'COA']
    elif product.startswith('LT5'):
        identifier = '3119'
        stations = ['GLC', 'ASA', 'KIR', 'MOR', 'KHC', 'PAC',
                    'KIS', 'CHM', 'LGS', 'MGR', 'COA', 'MPS', 'CUB']
    else:
        raise NotImplementedError('Must provide valid product string...')

    return identifier, stations


def find_valid_scene(ref_time, prow, sat, delta=16):
    scene_found = False

    possible_l7_stations = ['EDC', 'SGS', 'AGS', 'ASN', 'SG1', 'CUB', 'COA']
    possible_l8_stations = ['LGN']
    possible_l5_stations = ['PAC', 'GLC', 'ASA', 'KIR', 'MOR', 'KHC',
                            'KIS', 'CHM', 'LGS', 'MGR', 'COA', 'MPS', 'CUB']

    if sat == 'LC8':
        station_list = possible_l8_stations
    elif sat == 'LE7':
        station_list = possible_l7_stations
    elif sat == 'LT5':
        station_list = possible_l5_stations
    else:
        raise InvalidSatelliteError('Must provide valid satellite...')

    attempts = 0
    while attempts < 5:

        date_part = datetime.strftime(ref_time, '%Y%j')
        padded_pr = '{}{}'.format(str(prow[0]).zfill(3), str(prow[1]).zfill(3))

        if not scene_found:

            print 'Looking for version/station combination....'
            for archive in ['00', '01', '02']:

                for location in station_list:

                    scene_str = '{}{}{}{}{}'.format(sat, padded_pr, date_part, location, archive)

                    if web_tools.verify_landsat_scene_exists(scene_str):
                        version = archive
                        print 'using version: {}, location: {}'.format(version, location)
                        return padded_pr, date_part, location, archive

                if scene_found:
                    break

            if not scene_found:
                ref_time += timedelta(days=delta)
                print 'No scene, moving {} days ahead to {}'.format(delta, datetime.strftime(ref_time, '%Y%j'))
                attempts += 1

    raise StationNotFoundError('Did not find a valid scene within time frame.')


def assemble_scene_id_list(ref_time, prow, sat, end_date, delta=16):

    scene_id_list = []

    padded_pr, date_part, location, archive = find_valid_scene(ref_time, prow, sat)

    while ref_time < end_date:

        scene_str = '{}{}{}{}{}'.format(sat, padded_pr, date_part, location, archive)

        print 'add scene: {}, for {}'.format(scene_str,
                                             datetime.strftime(ref_time, '%Y-%m-%d'))
        scene_id_list.append(scene_str)

        ref_time += timedelta(days=delta)

        date_part = datetime.strftime(ref_time, '%Y%j')

    return scene_id_list


def get_candidate_scenes_list(path_row, sat_name, start_date, end_date):
    """
    
    :param path_row: path, datetime obj
    :param sat_name: 'LT5', 'LE7', or 'LC8'
    :param start_date: datetime object start image search
    :param end_date: datetime object finish image search
    :param max_cloud_cover: percent cloud cover according to USGS image metadata, float
    :param limit_scenes: max number scenese, int
    :return: reference overpass = str('YYYYDOY'), station str('XXX') len=3
    """

    reference_overpass = web_tools.landsat_overpass_time(path_row,
                                                         start_date, sat_name)

    scene_list = assemble_scene_id_list(reference_overpass, path_row, sat_name, end_date)
    return scene_list


def down_usgs_by_list(scene_list, output_dir, usgs_creds_txt):
    sat = scene_list[0][:3]

    usgs_creds = get_credentials(usgs_creds_txt)

    for product in scene_list:
        out_file = os.path.join(output_dir, product)
        download_chunks(sat, product, out_file, usgs_creds)
        unzip_image(out_file, output_dir)

    return None


if __name__ == '__main__':
    pass
# ===============================================================================
