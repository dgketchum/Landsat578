#!/usr/bin/env python

import os
import argparse
from osgeo import ogr
from datetime import datetime

from landsat import usgs_download
from vector_tools import get_pr_from_field, get_pr_multipath
from web_tools import convert_lat_lon_wrs2pr


def args_options():

    parser = argparse.ArgumentParser(prog='landsat')

    parser.add_argument('-s', '--start', help='Start date in format YYYY-MM-DD')
    parser.add_argument('-e', '--end', help='End date in format YYY-MM-DD')
    parser.add_argument('--satellite', help='Satellite name: LT5, LE7, or LC8')
    parser.add_argument('--lat', help='Latitude')
    parser.add_argument('--lon', help='Longitude')
    parser.add_argument('--path', help='The path')
    parser.add_argument('--row', help='The row')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('--shapefile', help='A shapefile with polygons (.shp)')
    parser.add_argument('--credentials',
                        help='Path to a text file with USGS credentials with one space between <username password>')
    parser.add_argument('--seek-multipath', help='Search for multiple paths within shapefile coverage')
    parser.add_argument('--return-list', help='Just return list of images without downloading')

    return parser


def main(args):
    if args:

        if args.lat:
            download_landsat((datetime.strptime(args.end, '%Y%M%d'), datetime.strptime(args.end, '%Y%M%d')),
                             args.satellite, lat_lon_tuple=(args.lat, args.lon), )


def download_landsat(start_end_tuple, satellite, path_row_tuple=None, lat_lon_tuple=None,
                     shape=None, output_path=None, seek_multipath=False, multipath_points=None,
                     usgs_creds=None):
    start_date, end_date = start_end_tuple[0], start_end_tuple[1]
    print 'Date range: {} to {}'.format(start_date, end_date)

    if shape and not seek_multipath:
        # assumes shapefile has a 'path' and a 'row' field
        ds = ogr.Open(shape)
        lyr = ds.GetLayer()
        image_index = get_pr_from_field(lyr)
        print 'Downloading landsat by shapefile: {}'.format(shape)

    elif seek_multipath:
        image_index = get_pr_multipath(multipath_points, shape)
        print 'Downloading landsat for multipath'
        print 'shapefile: {}'.format(shape)
        print 'points shapefile: {}'.format(multipath_points)

    elif lat_lon_tuple:
        # for case of lat and lon
        image_index = [convert_lat_lon_wrs2pr(lat_lon_tuple)]
        print 'Downloading landsat by lat/lon: {}'.format(lat_lon_tuple)

    elif path_row_tuple:
        # for case of given path row tuple
        image_index = [path_row_tuple]
        print 'Downloading landsat by path/row: {}'.format(path_row_tuple)

    else:
        raise NotImplementedError('Must give path/row tuple, lat/lon tuple plus row/path \n'
                                  'shapefile, or a path/rows shapefile!')

    print 'Image Ind: {}'.format(image_index)

    for tile in image_index:
        destination_path = os.path.join(output_path, 'd_{}_{}'.format(tile[0], tile[1]))

        if not os.path.exists(destination_path):
            print 'making dir: {}'.format(destination_path)
            os.mkdir(destination_path)

        scenes_list = usgs_download.get_candidate_scenes_list(tile, satellite, start, end)

        usgs_download.down_usgs_by_list(scenes_list, destination_path, usgs_creds)

    return None


if __name__ == '__main__':
    home = os.path.expanduser('~')
    start = datetime(2007, 5, 1)
    end = datetime(2007, 5, 30)
    sat = 'LT5'
    output = os.path.join(home, 'images', sat)
    usgs_creds = os.path.join(home, 'images', 'usgs.txt')
    path_row = 37, 27
    download_landsat((start, end), satellite=sat.replace('andsat_', ''),
                     path_row_tuple=path_row, output_path=output, usgs_creds=usgs_creds)


# ===============================================================================
