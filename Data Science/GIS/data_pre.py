# -*- coding: utf-8 -*-
"""
Created on Sat May  7 13:21:54 2016

@author: guoxuan

进行数据预先处理，把不规则数据处理成规则数据

关键变量为：
ID 识别个体信息
year 时间信息
province 省份
city     城市
county   县
address  地址

返回的是
lat    
lng
cofidence


"""

import pandas as pd 
import numpy as np
import re 
import geoBaidu

## load the data 
# data=pd.read_stata("F:\\2003.dta") ## 编码有问题

data=pd.read_csv("F:\\2003_utf8.txt",encoding='utf-8',sep='\t')
data2=pd.read_csv("F:\\2003_utf8.csv",encoding='utf-8',sep='\t')

## ----------------------------------------------------
## 分列
## ----------------------------------------------------
col=data2.columns[0]
data_new=data2[col].str[1:-1].str.split(',', return_type='frame')
data_new.drop(labels=data_new.columns[-1],axis=1,inplace=True)


cols=col.split(',')
old_cols=data_new.columns.tolist()
new_cols=['address','region_code','id','province','city','county']
data_new.rename(columns=dict(zip(old_cols, new_cols)), inplace=True)




## 获取地理位置信息

Baidu=geoBaidu.geoBaidu(ak='DPlowD7PIEfaVtpxLKGkXg8yDCCBanVO')


def get_geocoding(df):
    id_index=df['id']
    query=df[['address','county','city','province']]
    output=Baidu.geocode(query)
    [lat,lng]=output.latlng
    confidence=output.confidence
    return (id_index,lat,lng,confidence)
 

geo_info=Baidu.geocode(data_new.loc[2,['address','county','city','province']].tolist())

gis_result=get_geocoding(data_new.loc[2,:])

#temp_list=map(get_geocoding,data_new.loc[0:10,:])

geo_info=pd.DataFrame(columns=['id','lat','lng','confidence'])

percent=1
for i in range(0,int(len(data_new)*percent)):
    geo_info.loc[i,]=get_geocoding(data_new.loc[i,:])

# get the gis info from data  
geo_info.to_csv("F:\\geo_2003.csv",index=False)

total_df=pd.merge(geo_info,data_new,on='id',how='inner')
total_df.to_csv("F:\\total_2003.csv",index=False)


## map 
## note that map(func, list1,list2,list3) 
## stop the dataframe input 

## but pandas maybe support map 

