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
land_map.create_map('land_map.html')
land_map


##----------------------------------------------------------------------------
## Choropleth Maps

##----------------------------------------------------------------------------

import folium
import pandas as pd
import json

path='F:/github/Project/data visualization/'


## US example
state_geo = r'geojson/us-states.json'
state_unemployment = r'data/US_Unemployment_Oct2012.csv'

state_data = pd.read_csv(state_unemployment)

#Let Folium determine the scale
states = folium.Map(location=[48, -102], zoom_start=3)
states.geo_json(geo_path=state_geo, data=state_data,
                columns=['State', 'Unemployment'],
                key_on='feature.id',
                fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
                legend_name='Unemployment Rate (%)')
states.create_map(path='us_state_map.html')
#Let's define our own scale and change the line opacity
states2 = folium.Map(location=[48, -102], zoom_start=3)
states2.geo_json(geo_path=state_geo, data=state_data,
                 columns=['State', 'Unemployment'],
                 threshold_scale=[5, 6, 7, 8, 9, 10],
                 key_on='feature.id',
                 fill_color='BuPu', fill_opacity=0.7, line_opacity=0.5,
                 legend_name='Unemployment Rate (%)',
                 reset=True)
states2.create_map(path='us_state_map_2.html')

## read the json file 
#df_json=pd.read_json(path+state_geo)
data_cn_json=open(path+china_geo,encoding='utf-8').read()
data=json.loads(data_cn_json)
df_cn_json=pd.DataFrame(data['features'])

data_us_json=open(path+state_geo,encoding='utf-8').read()
data=json.loads(data_us_json)
df_us_json=pd.DataFrame(data['features'])

## delete element  and add element
data_cn_json=open(path+'geojson/chn_adm1.json',encoding='utf-8').read()
data=json.loads(data_cn_json)
data1=data['features']
for i in range(len(data1)): 
    try:
        data1[i]['type']='Feature'
        del data1[i]['properties']['NL_NAME_1'] 
        del  data1[i]['properties']['VARNAME_1'] 
        
        
    except :
        pass
data['type']='FeatureCollection'
data['features']=data1

f=open('geojson/chn_adm1_2.json','w')
#f.write(json.dumps(data))
json.dump(data,f)
f.close()


## China Example
china_geo=r'geojson/chn_adm1_2.json'
CN_unemployment = r'data/CN-demo.csv'

state_data = pd.read_csv(CN_unemployment)

#Let Folium determine the scale
map_ch = folium.Map(location=[48, 120], zoom_start=3)
map_ch.geo_json(geo_path=china_geo, data=state_data,
             columns=['State', 'Unemployment'],
             key_on='feature.properties.HASC_1',
             fill_color='YlGn', fill_opacity=0.7, line_opacity=0.2,
             legend_name='Unemployment Rate (%)')
map_ch.create_map('cn_states.html')

csv_data = r'data/CN-gdp-2014.csv'
state_data = pd.read_csv(csv_data,encoding='gbk')
map_ch = folium.Map(location=[50, 120], zoom_start=3)
map_ch.geo_json(geo_path=china_geo, data=state_data,
             columns=['province', 'GDP-2014'],
             #threshold_scale=[6, 7, 8, 9, 10,11,12,13],
             key_on='feature.properties.HASC_1',
             fill_color='BuPu', fill_opacity=0.7, line_opacity=0.5,
             legend_name='GDP Rate (%)',reset=True)
map_ch.create_map('cn_states2.html')