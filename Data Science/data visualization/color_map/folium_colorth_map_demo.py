# -*- coding: utf-8 -*-
"""

@author: guoxuan

map visualization demo by folium

source 
http://code.highcharts.com/mapdata/

draw Choropleth Maps

"""

import folium
import pandas as pd
import json

path='your path to the directory'


## China Example
china_geo=r'geojson/chn_adm1_2.json'
CN_unemployment = r'data/CN-demo.csv'

state_data = pd.read_csv(path+CN_unemployment)

#draw Unemployment
map_ch = folium.Map(location=[48, 120], zoom_start=3)
map_ch.choropleth(geo_data=path+china_geo, data=state_data,
             columns=['State', 'Unemployment'],
             key_on='feature.properties.HASC_1',
             fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
             legend_name='Unemployment Rate (%)')
map_ch.save(path+'cn_states.html')

#draw GDP
csv_data = r'data/CN-gdp-2014.csv'
state_data = pd.read_csv(path+csv_data,encoding='gbk')
map_ch = folium.Map(location=[50, 120], zoom_start=3)
map_ch.choropleth(geo_data=path+china_geo, data=state_data,
             columns=['province', 'GDP-2014'],
             #threshold_scale=[6, 7, 8, 9, 10,11,12,13],
             key_on='feature.properties.HASC_1',
             fill_color='BuPu', fill_opacity=0.7, line_opacity=0.5,
             legend_name='GDP Rate (%)',reset=True)
map_ch.save(path+'cn_states2.html')