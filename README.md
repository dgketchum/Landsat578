# ![Landsat](data/maple.png)

[![Build Status](https://travis-ci.org/dgketchum/Landsat578.svg?branch=master)](https://travis-ci.org/dgketchum/Landsat578)

# Easy Landsat Download

Download and unzip Landsat 5, 7, and 8 (a.k.a. LT5, LE7, LC8) images 
via the USGS website automatically using a command line interface or 
a simple python script.

## Install
To get the package from PyPi:
```
$ pip install Landsat578
```

To get the package with conda:
```
$ conda install Landsat578
```

Landsat instruments orbit the earth in sun-synchronous fashion.
They pass over each place at approximately the same 
time of day, every 16 days. The area within each image is
predefined and is described by (path,row) coordinates of
the World Reference System 2 (WRS2).
This system applies to all Landsat missions since LT4.
Every place on Earth falls under at lease one path/row 'scene.'
Some places fall within overlapping path/row scenes.

See WRS2 over the US state of Montana. Scene 38, 27 is highlighted
in purple. Note overlap of neighboring scenes.

# ![Landsat](data/MJ_tile.png)


# Run

If you know the path and row of a location, you can enter it in the 
command line interface to download and unzip images there between
your specified start and end dates.  You must choose a satellite.
Within the package you downloaded, you need to call landsat_download.py.
Dates are entered as YYYY-MM-DD format, e.g. 2008-05-31.

```
$ landsat_download.py LE7 2007-05-01 2007-05-31 --path 38 --row 27
```
This command will find the two images that were captured by Landsat
5 of scene 38, 27 in the month of May, 2007 and unzip them.
Use the optional parameter ```--return-list``` to just get a list
of what was found:


```
$ landsat_download.py LE7 2007-05-01 2007-05-31 --path 38 --row 27 --returm-list
```

This will return the two image scene IDs and print to your screen.

```
['LE70360292007122EDC00', 'LE70360292007138EDC00']
```

The naming conventions of Landsat images are as follows from
the usgs Landsat [site.](https://landsat.usgs.gov/what-are-naming-conventions-landsat-scene-identifiers)


# ![Landsat](data/landsat_names.png)


# 2017 dgetchum

