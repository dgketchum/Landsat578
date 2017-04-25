import os
from datetime import datetime

from landsat import downloader

if __name__ == '__main__':
    home = os.path.expanduser('~')
    start = datetime(2007, 5, 1)
    end = datetime(2007, 5, 30)
    satellite = 'LT5'
    output = os.path.join(home, 'images', satellite)
    usgs_creds = os.path.join(home, 'images', 'usgs.txt')
    path = 37
    row = 27
    latitude = None
    longitude = None
    shapefile = None
    downloader.download_landsat((start, end), satellite, path_row_tuple=(path, row),
                                output_path=output, usgs_creds=usgs_creds, dry_run=False)

# ===============================================================================
