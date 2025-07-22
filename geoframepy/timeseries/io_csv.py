# -*- coding: utf-8 -*-
"""
Created on Tue August 10 2021

/*
 * GNU GPL v3 License (by, nc, nd, sa)
 *
 * Copyright 2021 GEOframe group
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

import os as os
import pandas as pd
import numpy as np
from datetime import datetime


def pandas_read_OMS_timeseries(file_name, **kwargs):
    r'''
    Read a timeseries .csv file formatted for OMS console
   
    :param file_name:
        file name of the csv file.
    :type file_name: string
   
    :param nan_value:
        value used for no values.
    :type nan_value: double

    :param \**kwargs:
    See below
    
    :Keyword Arguments
        * *na_values* float, default -9999
             no value
            
        * *datetime_index* bool, default True 
            to get date time column as index, False vice-versa
        * *parse_dates* bool, default True


    :return pandas dataframe
   
    @author: Niccolò Tubini
    '''

    na_values = kwargs.get('nan_values',-9999)
    datetime_index = kwargs.get('datetime_index',True)
    parse_dates = kwargs.get('parse_dates',True)
    
    df = pd.read_csv(file_name,skiprows=3,header=1,low_memory=False)
    df = df.drop(['ID'],axis=1)
    df = df.drop([0,1],axis=0)
    df.columns.values[0] = 'Datetime'
    if(parse_dates==True):
        try:
            df['Datetime'] = pd.to_datetime(df['Datetime'])
        except Exception as error:
            print("An exception occurred: {error}")
    if(datetime_index==True):
        df.set_index('Datetime', inplace = True)
        df = df.astype('float64', copy = True)
        df[df <= na_values]=np.nan 
    else:
        df.reset_index(drop=True, inplace=True)
        df.iloc[:,1:] = df.iloc[:,1:].astype('float64', copy = True)
        df[df.iloc[:,1:] <= na_values]=np.nan 
   
    return df



def write_OMS_timeseries(df, file_name, **kwargs):
    '''
    Save a timeseries dataframe to .csv file with OMS format
   
    :param df: dataframe containing the timeseries. Each column correspond to a station/centroid and the 
    the header contains the ID of the station/centroid.
    :type df: pandas.dataframe
   
    :param file_name: output file name.
    :type file_name: str
    
    :param \**kwargs:
    See below
    
    :Keyword Arguments
        * *has_datetime* bool, default True
             if the dataframe has datetime index True, otherwise False
            
        * *start_date* str, '01-01-2020 00:00' 
            start date of the timeseries. 'mm-dd-yyyy hh:mm'
            
        * *frequency* str, default '1H'    
            frequency of the timeseries. 'H': hourly, 'D': daily

    @author: Niccolò Tubini
    
    Notes:
    2021-01-09 changed pd.date_range with pd.period_range 
    https://stackoverflow.com/questions/50265288/how-to-work-around-python-pandas-dataframes-out-of-bounds-nanosecond-timestamp
    '''
    has_datetime = kwargs.get('has_datetime',True)
    start_date = kwargs.get('start_date','01-01-2020 00:00')
    frequency = kwargs.get('frequency','1H')

    if has_datetime==True:
        df.reset_index(inplace=True)
        df[df.columns[0]] = pd.to_datetime(df[df.columns[0]]).dt.strftime('%Y-%m-%d %H:%M')
        df = df.astype(str)
    else:
        df = df.astype(str)
        date_rng = pd.period_range(start=start_date, periods=df.shape[0], freq=frequency).strftime('%Y-%m-%d %H:%M')
        df_dates = pd.DataFrame(date_rng, columns=['date'])
        df = pd.concat([df_dates, df],sort=False, axis=1)
    
    df.replace('nan','-9999',inplace = True)
    df.replace('-9999.0','-9999',inplace = True)
    
    n_col = df.shape[1]
    value = []
    ID = []
    double = []
    commas = []
    for i in range(1,n_col):
        value.append(',value_'+str(df.columns[i]))
        ID.append(','+str(df.columns[i]))
        double.append(',double')
        commas.append(',')
   
    line_4 = '@H,timestamp'+''.join(value) + '\n'
    line_5 = 'ID,'+''.join(ID) + '\n'
    line_6 = 'Type,Date' + ''.join(double) + '\n'
    line_7 = 'Format,yyyy-MM-dd HH:mm' + ''.join(commas) + '\n'

    date = datetime.today().strftime('%Y-%m-%d %H:%M')
    df.insert(loc=0, column='-', value=np.nan)
    with open(file_name,'w') as file:
        file.write('@T,table\nCreated,'+ date +'\nAuthor,HortonMachine library\n')
        file.write(line_4)
        file.write(line_5)
        file.write(line_6)
        file.write(line_7)
    df.to_csv(file_name, header=False, index=False, mode="a")
    print ('\n\n***SUCCESS writing!  '+ file_name)