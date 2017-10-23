import os
from datetime import datetime

from landsat import download_composer

if __name__ == '__main__':
    home = os.path.expanduser('~')
    start = datetime(2015, 6, 1)
    end = datetime(2015, 6, 10)
    satellite = 'LC8'
    output = os.path.join(home, 'images', 'LC8', 'cloud_test')
    usgs_creds = os.path.join(home, 'images', 'usgs.txt')
    path = 41
    row = 27
    # latitude = 45.6
    # longitude = -107.9
    download_composer.download_landsat((start, end), satellite,
                                       path_row_list=[(path, row)],
                                       output_path=output,
                                       usgs_creds=usgs_creds)

# ===============================================================================
