# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 21:00:31 2016

data visualization: 

gis map 

environment: python 3
tools: vincent 


@author: guoxuan
"""

import vincent 

world_topo = r'world-countries.topo.json'
geo_data = [{'name': 'countries',
             'url': world_topo,
             'feature': 'world-countries'}]

vis = Map(geo_data=geo_data, scale=200)