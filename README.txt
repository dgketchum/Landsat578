DEPRECATED, October 2026: Landsat578 downloaded Landsat Collection 1 scenes from the Google Cloud public bucket. USGS stopped producing Collection 1 at the end of 2021 and removed it from its archive in December 2022; the Google bucket is a frozen copy with no Landsat 9 and nothing acquired after 2021. This repository is archived and will not be updated. For Collection 2 data, query the USGS LandsatLook STAC API (https://landsatlook.usgs.gov/stac-server) with pystac-client and download with a tool such as eodag or stac-asset; for analysis-ready access use Google Earth Engine or odc-stac. The text below is kept as a historical record.

Update July 4, 2024:

Revisiting this package for a new project, found that GCS only
updated Landsat images until sometime in 2021. I got this running
again and updated to modern Python packages for this push. AWS is now
charging 'requestor pays' to download from their public storage. I think
it will be necessary to get a machine-to-machine API key from USGS
Earth Explorer to download recent imagery for the time being. YMMV.

Download and unzip Landsat 5, 7, and 8 (a.k.a. LT5, LE7, LC8) images
via the Google service automatically using a command line interface or
a simple python script. (Now you can get all Landsat [1, 2, 3, 4, 5, 7, 8]!)

Python 3.9 compatible.

Landsat instruments orbit the earth in sun-synchronous fashion.
They pass over each place at approximately the same
time of day, every 16 days. The area within each image is
predefined and is described by (path,row) coordinates of
the World Reference System 2 (WRS2).
This system applies to all Landsat missions since LT4.
Every place on Earth falls under at lease one path/row 'scene.'
Some places fall within overlapping path/row scenes. Landsat
'descends' from North to South in the day, these images are of
most interest to researchers, though nighttime images are also
available.

The first time running this code will download and package a large
list of scenes. This should thereafter be updated if one is after
the latest imagery.  This is a large file and will need about 3GB
memory available to the python process to process it.

landsat --update-scenes

It will also download the needed WRS shapefiles that will help locate
the path and row of given coordinates.

If you know the path and row of a location, you can enter it in the
command line interface to download and unzip images there between
your specified start and end dates.  You must choose a satellite.
Within the package you downloaded, you need to call landsat.py.
Dates are entered as YYYY-MM-DD format, e.g. 2008-05-31.