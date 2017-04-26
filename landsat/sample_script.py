import os
from datetime import datetime

from landsat import download_composer

if __name__ == '__main__':
    home = os.path.expanduser('~')
    start = datetime(2007, 5, 1)
    end = datetime(2007, 5, 30)
    satellite = 'LT5'
    output = os.path.join(home, 'images', satellite)
    usgs_creds = os.path.join(home, 'images', 'usgs.txt')
    # path = 37
    # row = 27
    latitude = 45.6
    longitude = -107.9
    download_composer.download_landsat((start, end), satellite, lat_lon_tuple=(latitude, longitude),
                                       output_path=output, usgs_creds=usgs_creds, dry_run=False)

# ===============================================================================
