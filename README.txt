Download and unzip Landsat 5, 7, and 8 (a.k.a. LT5, LE7, LC8) images
via the Google service automatically using a command line interface or
a simple python script. (Now you can get all Landsat [1, 2, 3, 4, 5, 7, 8]!)

Python 2.7 and 3.6 compatible.

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