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
the World Reference System 2(WRS2).
This system applies to all Landsat missions since LT4.
Every place on Earth falls under at lease one path/row 'scene.'
Some places fall within overlapping path/row scenes.

See WRS2 over the US state of Montana. Scene 38, 27 is highlighted
in purple. Note overlap of neighboring scenes.

# ![Landsat](data/MJ_tile.png)

# 2017 dgetchum

