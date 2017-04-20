# ===============================================================================
# Copyright 2017 dgketchum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
import os
from osgeo import gdal, osr, ogr


def shp_proj4_spatial_reference(shapefile):
    """Get spatial reference from an ESRI .shp shapefile

    :param shapefile: ESRI type .shp
    :param definition_type: osr.SpatialReference type
    :return: spatial reference in specified format
    """
    ds = ogr.Open(shapefile)
    layer = ds.GetLayer()
    layer_srs = layer.GetSpatialRef()
    comp = layer_srs.ExportToProj4()
    return comp


def tif_proj4_spatial_reference(raster):
    if not os.path.isfile(raster):
        raise NotImplementedError('Raster file not found.')
    dataset = gdal.Open(raster)
    wkt = dataset.GetProjection()
    srs = osr.SpatialReference()
    srs.ImportFromWkt(wkt)
    proj4 = srs.ExportToProj4()
    return proj4


def get_raster_geo_attributes(root):
    """
    Creates a dict of geographic attributes from a .tif raster.

    :param root: Path to a folder with pre-processed standardized rasters.
    :return: dict of geographic attributes.
    """

    if os.path.isdir(root):
        file_name = next((fn for fn in os.listdir(root) if fn.endswith('.tif')), None)
    elif os.path.isfile(root):
        file_name = root
    else:
        raise NotImplementedError('Must pass a dir with .tif files or a .tif file.')

    dataset = gdal.Open(os.path.join(root, file_name))

    band = dataset.GetRasterBand(1)

    raster_geo_dict = {'cols': dataset.RasterXSize, 'rows': dataset.RasterYSize,
                       'bands': dataset.RasterCount,
                       'data_type': band.DataType,
                       'projection': dataset.GetProjection(),
                       'srs': tif_proj4_spatial_reference(file_name),
                       'geotransform': dataset.GetGeoTransform(),
                       'resolution': dataset.GetGeoTransform()[1]}

    return raster_geo_dict


def check_same_reference_system(first_geo, second_geo):
    if first_geo.endswith('.tif'):
        first_srs = tif_proj4_spatial_reference(first_geo)
    elif first_geo.endswith('.shp'):
        first_srs = shp_proj4_spatial_reference(first_geo)
    else:
        raise NotImplementedError('Must provide either shapefile or tif raster.')

    if second_geo.endswith('.tif'):
        second_srs = tif_proj4_spatial_reference(second_geo)
    elif second_geo.endswith('.shp'):
        second_srs = shp_proj4_spatial_reference(second_geo)
    else:
        raise NotImplementedError('Must provide either shapefile or tif raster.')

    if first_srs == second_srs:
        return True
    else:
        return False


if __name__ == '__main__':
    pass

# ===============================================================================
