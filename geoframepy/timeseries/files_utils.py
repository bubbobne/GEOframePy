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
import os

import networkx as nx
import pandas as pd
from geoframepy.timeseries.io_csv import write_OMS_timeseries


def process_network_to_timeseries(net, root_path, start_date, end_date, dt, nan=-9999.0):
    """
    Processes a network and generates timeseries data for each node, saving the files in the specified root path.

    :param nan: no data value
    :param dt: the time step
    :param end_date:
    :param start_date:
    :param net: A directed graph represented as a NetworkX DiGraph object.
    :param root_path: The root path where the timeseries files will be saved.
    :return: None. The function writes timeseries data to files in the specified root path.
    """
    subbasins_id = list(net.nodes)

    for ids in subbasins_id:
        date = pd.date_range(start=start_date, end=end_date, freq=dt)
        df_tmp = pd.DataFrame(date, columns=['Datetime'])
        df_tmp['val'] = nan
        df_tmp.set_index('Datetime', inplace=True)
        #if dt == "H":
        df_tmp.index = df_tmp.index.strftime('%Y-%m-%d %H:%M')
        #elif dt == "D":
            #df_tmp.index = df_tmp.index.strftime('%Y-%m-%d')

        df_tmp.columns = [str(ids)]
        output_path = f"{root_path}/{str(ids)}/Nan_{str(ids)}.csv"
        print(output_path)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_OMS_timeseries(df_tmp.iloc[:, :], output_path, has_datetime=True)
