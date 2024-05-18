# -*- coding: utf-8 -*-
"""
Created on Tue August 10 2021

/*
 * GNU GPL v3 License (by, nc, nd, sa)
 *
 * Copyright 2024 GEOframe group
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

@author: GEOframe group
"""
import rasterio as rasterio
from shapely.geometry import shape, mapping
import fiona
import os
from fiona.crs import from_epsg
from shapely import geometry, ops
import shutil


def clone_shape_file(base_folder, source_shapefile_path, basin_id):
    """
    Clone the centroid shapefile
    :base_folder
    :source_shapefile_path
    :basin_id

    @author: Daniele Andreis
    """
    # Define the paths to the source (existing) shapefile and the destination (new) shapefile
    destination_shapefile_path = base_folder + "centroid_ID_old_" + basin_id + ".shp"
    # Copy the source shapefile to the destination using shutil
    shutil.copy(source_shapefile_path, destination_shapefile_path)
    shutil.copy(source_shapefile_path.replace('.shp', '.shx'), destination_shapefile_path.replace('.shp', '.shx'))
    shutil.copy(source_shapefile_path.replace('.shp', '.dbf'), destination_shapefile_path.replace('.shp', '.dbf'))
    shutil.copy(source_shapefile_path.replace('.shp', '.prj'), destination_shapefile_path.replace('.shp', '.prj'))
    print(f'Shapefile copied as {destination_shapefile_path}')


def check_centroid(path, crs_code, do_new_point):
    """
    Check if the centroid is inside the polygon for each subbasins. :path the path containing the subbasins folder
    :crs_code the reference cordinate system (as integer value e.g. 32632 ) :do_new_point if true create a new
    centroid shapefile, rename the old one. Otherwise only print the id of sub-basins with problem.

    @author: Daniele Andreis
    """
    folders = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            folders.append(item)

    for folder in folders:
        my_centroid = fiona.open(path + folder + "/centroid_ID_" + folder + ".shp")
        first = next(iter(my_centroid))
        point = shape(first['geometry'])
        polygons = fiona.open(path + folder + "/subbasins_complete_ID_" + folder + ".shp")
        first = next(iter(polygons))
        polygon = shape(first['geometry'])
        if not polygon.contains(point):
            clone_shape_file(path + folder + "/", path + folder + "/centroid_ID_" + folder + ".shp", folder)
            print(folder)
            net_shp = path + folder + "/network_complete_ID_" + folder + ".shp"
            file_exists = os.path.exists(net_shp)
            # thanks to @Helios
            if file_exists and do_new_point:
                net = fiona.open(net_shp)
                multiline = []
                for f in iter(net):
                    multiline.append(shape(f['geometry']))
                    multi_line = geometry.MultiLineString(multiline)
                    merged_line = ops.linemerge(multi_line)
                new_centroid = merged_line.representative_point()
                output_shapefile = path + folder + "/centroid_ID_" + folder + ".shp"
                schema = {'geometry': 'Point',
                          'properties': {'basinid': 'int', 'centrx': 'float', 'centry': 'float', 'elev_m': 'float',
                                         'avgelev_m': 'float', 'area_km2': 'float', 'length_m': 'float',
                                         'skyview': 'float'}}
                crs = from_epsg(crs_code)
                my_geometry = mapping(new_centroid)
                x_coord, y_coord = my_geometry['coordinates']

                with rasterio.open(path + folder + "/dtm_" + folder + ".asc") as src:
                    values = list(src.sample([my_geometry['coordinates']]))  # Returns a list of values at the geometry
                    if my_geometry['type'] == 'Point':
                        elev = float(values[0][0])
                        print("Raster Values:", elev)

                with rasterio.open(path + folder + "/sky_" + folder + ".asc") as src:
                    values = list(src.sample([my_geometry['coordinates']]))  # Returns a list of values at the geometry
                    if my_geometry['type'] == 'Point':
                        sky = float(values[0][0])
                        print("Raster Values:", sky)

                with fiona.open(output_shapefile, 'w', 'ESRI Shapefile', schema, crs=crs) as output:
                    feature = {
                        'geometry': my_geometry,
                        'properties': {'basinid': int(folder), 'centrx': float(x_coord), 'centry': float(y_coord),
                                       'elev_m': elev,
                                       'avgelev_m': first['properties']['avgelev_m'],
                                       'area_km2': first['properties']['area_km2'],
                                       'length_m': first['properties']['length_m'],
                                       'skyview': sky}
                    }
                    output.write(feature)
            else:
                print("network not found")
