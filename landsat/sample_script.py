import os
from datetime import datetime

import download_composer

if __name__ == '__main__':
    home = os.path.expanduser('~')
    start = datetime(2014, 6, 1)
    end = datetime(2014, 6, 30)
    satellite = 'LC8'
    output = os.path.join(home, 'images', satellite)
    usgs_creds = os.path.join(home, 'images', 'usgs.txt')
    # path = 37
    # row = 27
    latitude = 45.6
    longitude = -107.9
    download_composer.download_landsat((start, end), satellite, latitude=latitude, longitude=longitude,
                                       output_path=output, usgs_creds=usgs_creds)

# ===============================================================================
