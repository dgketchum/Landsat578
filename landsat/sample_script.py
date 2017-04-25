import os
from datetime import datetime

from landsat import downloader


def get_landsat((start, end), satellite, (path, row), (lat, lon), shape, usgs_creds,
                dry_run):

    downloader.download_landsat((start, end), satellite, path_row_tuple=(path, row),
                                output_path=output, usgs_creds=usgs_creds, dry_run=False)

if __name__ == '__main__':
    home = os.path.expanduser('~')
    start = datetime(2007, 5, 1)
    end = datetime(2007, 5, 30)
    satellite = 'LT5'
    output = os.path.join('images',)
    usgs_creds = os.path.join('usgs.txt')
    path_row = 37, 27

# ===============================================================================
