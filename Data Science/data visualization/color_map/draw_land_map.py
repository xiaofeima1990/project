# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 22:32:12 2016

@author: guoxuan

map visualization demo 

source 
http://code.highcharts.com/mapdata/

"""

import folium
import pandas as pd

# Get a basic world map.
land_map = folium.Map(location=[40, 120], zoom_start=4)

# get the land gis data
path='.\\data\\'
data_file='gis-2015-12.csv'
data=pd.read_csv(path+data_file,encoding='gbk')

# Draw markers on the map.

for i in range(100):
    loc = data.loc[i,['lat','lng','new_ID']]
    land_map.circle_marker(location=[loc["lat"], loc["lng"]], popup=str(loc["new_ID"]))
# Create and show the map.
land_map.save(path+'land_map.html')


