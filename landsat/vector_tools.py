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
from osgeo import ogr, osr
from spatial_reference_tools import shp_proj4_spatial_reference


def lat_lon_to_ogr_point(lon, lat):
    """ Converts (lon, lat) to ogr Geometry
    :param lon: Longitude, float
    :param lat: Latitude, float
    :return: osgeo.ogr.Geometry
    """
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)
    return point


def points_to_shapefile(field_attr_dict, output_file, dst_srs_epsg=4326):
    """ Converts dict of point coordinates and attributes to point shapefile.
    :param field_attr_dict: dict of dicts e.g. {'1': {'LAT': 23.5, 'LON': -110.1, 'ATTR1': 4.}}
    :param output_file: .shp ESRI shapefile
    :param dst_srs_epsg: EPSG spatial reference system code (spatialreference.org)
    :return: None
    """
    if dst_srs_epsg:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(dst_srs_epsg)
    else:
        srs = None

    driver = ogr.GetDriverByName('Esri Shapefile')

    ds = driver.CreateDataSource(output_file)
    layer = ds.CreateLayer('Points_DGK', srs, ogr.wkbPoint)
    layer.CreateField(ogr.FieldDefn('FID', ogr.OFTString))
    for key in field_attr_dict['1'].keys():
        layer.CreateField(ogr.FieldDefn(key, ogr.OFTString))
    defn = layer.GetLayerDefn()

    for key, val in field_attr_dict.iteritems():
        feature = ogr.Feature(defn)
        wkt = 'POINT({} {})'.format(val['LON'], val['LAT'])
        point = ogr.CreateGeometryFromWkt(wkt)

        for field_name, field_value in val.iteritems():
            feature.SetField(field_name, str(field_value))
        feature.SetField('FID', key)
        feature.SetGeometry(point)
        layer.CreateFeature(feature)
        feature = None

    return None


def points_to_ogr_polygon(args):
    """ Converts list of point tuples [(lon, lat)] to polygon geometry.
    :param args: List of point tuples i.e. [(-110., 45.3), (-109.5, 46.1)]
    :return: osgeo.ogr.Geometry (polygon)
    """
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for point in args:
        ring.AddPoint(point[0], point[1])
    ring_poly = ogr.Geometry(ogr.wkbPolygon)
    ring_poly.AddGeometry(ring)
    return ring_poly


def shp_poly_to_pts_list(poli, include_z_vals=False):
    """ Converts polygon from shapefile to list of vertex coordinates.

    :param poli: ESRI shapefile with polygon
    :param include_z_vals: Include elevation values
    :return: List of coordinate tuples [(lon, lat)]
    """

    ds = ogr.Open(poli)
    layer1 = ds.GetLayer()
    print layer1.GetExtent()
    for feat in layer1:
        geom = feat.GetGeometryRef()
        ring = geom.GetGeometryRef(0)
        point_ct = ring.GetPointCount()
    points = []
    for p in xrange(point_ct):
        longi, lati, z = ring.GetPoint(p)
        points.append((longi, lati, z))
        if include_z_vals:
            print 'Points from shape: {}'.format(points)
            return points
    longlat = []
    for ll in points:
        lati, longi = ll[0], ll[1]
        longlat.append((longi, lati))
    print 'Points x, y from shape: {}'.format(longlat)
    return longlat


def poly_to_shp(polygon, output_file, field_attr_dict=None, dst_srs_epsg=4326):
    """ Converts ogr.Geometry polygon to shapefile.

    :param polygons: org.Geometry of polygon type
    :param output_file: path to save .shp
    :param field_attr_dict: dict of dicts e.g. {'1': {'FOO': 23.5, 'BAR': -110.1, 'ATTR1': 4.}}
    :param dst_srs_epsg: EPSG spatial reference system code (spatialreference.org)
    :return: None
    """
    if dst_srs_epsg:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(dst_srs_epsg)
    else:
        srs = None

    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(output_file)
    layer = ds.CreateLayer('', srs, ogr.wkbPolygon)

    for key, val in field_attr_dict['1'].iteritems():
        if isinstance(val, float):
            layer.CreateField(ogr.FieldDefn(key, ogr.OFTReal))
        elif isinstance(val, str):
            layer.CreateField(ogr.FieldDefn(key, ogr.OFTString))
        elif isinstance(val, int):
            layer.CreateField(ogr.FieldDefn(key, ogr.OFTInteger))
        else:
            raise TypeError('Found attribute of unknown type!')

    defn = layer.GetLayerDefn()

    for key, val in field_attr_dict.iteritems():
        feature = ogr.Feature(defn)

        for field_name, field_value in val.iteritems():
            feature.SetField(field_name, str(field_value))

        feature.SetField('FID', str(key))
        feature.SetGeometry(polygon)
        layer.CreateFeature(feature)
        feature = None

    return None


def shp_to_ogr_features(shape):
    """ Convert shapefile features to ogr.Feature list
    :param shape: ESRI Shapefile .shp
    :return: List of ogr.Feature features
    """
    reader = ogr.Open(shape)
    layer = reader.GetLayer()
    features = []
    for i in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(i)
        features.append(feature)
    return features


def shp_to_ogr_geometries(shape):
    """ Convert shapefile to list of geometries
    :param shape: ESRI Shapefile .shp
    :return: list of ogr.Geometry
    """
    ds = ogr.Open(shape)
    lyr = ds.GetLayer()
    geometries = []
    for feature in lyr:
        geom = feature.GetGeometryRef()
        geometries.append(geom)
    return geometries


def shp_to_attr_dict(shapefile):
    """Create a nested dict of attributes {FID: {ATTR1: X, ATTR2: Y}}
    :param shapefile: ESRI Shapefile .shp
    :return: Dict of attributes by ID
    """
    ds = ogr.Open(shapefile)
    lyr = ds.GetLayer()
    defn = lyr.GetLayerDefn()
    fields_dct = {}
    for field in xrange(defn.GetFieldCount()):
        f_name = defn.GetFieldDefn(field).GetName()
        fields_dct[f_name] = None

    shp_dct = {}
    for i, feature in enumerate(lyr):
        sub_dct = {}
        for key in fields_dct.keys():
            attr_value = feature.GetField(key)
            sub_dct[key] = attr_value
        shp_dct[str(i + 1)] = sub_dct
    return shp_dct


def get_pr_from_field(shapefile):
    """ Get PATH, ROW from shapefile attributes
    :param shapefile: ESRI Shapefile with PATH, ROW attributes
    :return: list of (path, row) tuples
    """
    dct = shp_to_attr_dict(shapefile)
    path_list = []
    for val in dct.itervalues():
        path = str(val['PATH'])
        row = str(val['ROW'])
        path_list.append((path.rjust(3, '0'), row.rjust(3, '0')))
    print path_list
    return path_list


def get_pr_multipath(points, poly_shapefile):
    """ Finds coincident point(s) intersection with shapefile polygons, makes list (path, row) tuples
    :param points: tuple, list of tuples, points ESRI shapefile
    :param poly_shapefile: ESRI shapefile of Landsat path, row
    :return: List of path, row tuples
    """
    path_list = []

    poly_features = shp_to_ogr_features(poly_shapefile)
    poly_geo_refs = [pl.GetGeometryRef() for pl in poly_features]
    poly_srs = shp_proj4_spatial_reference(poly_shapefile)

    if isinstance(points, tuple):
        pt_geo_refs = [lat_lon_to_ogr_point(points[0], points[1])]
    elif isinstance(points, list):
        pt_geo_refs = []
        for pt in points:
            pt_geo_refs.append(lat_lon_to_ogr_point(pt[0], pt[1]))
    elif isinstance(points, str):
        pt_features = shp_to_ogr_features(points)
        pt_geo_refs = [pt.GetGeometryRef() for pt in pt_features]
        point_srs = shp_proj4_spatial_reference(points)
        print 'Poly and Point SRS same: {}'.format(poly_srs == point_srs)
    else:
        raise NotImplementedError('Function takes first arg type tuple, list, or string')

    for point in pt_geo_refs:
        for j, polygon in enumerate(poly_geo_refs):
            if point.Within(polygon):
                path, row = poly_features[j].GetField('PATH'), poly_features[j].GetField('ROW')
                if (path, row) not in path_list:
                    path_list.append((path, row))

    return path_list


if __name__ == '__main__':
    pass

# ===============================================================================
