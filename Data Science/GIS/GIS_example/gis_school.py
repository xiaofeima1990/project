# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 22:10:33 2017

@author: guoxuan
"""

#import geopy
path="D:\\temp\\"
file_name='school_name.txt'

from geopy.geocoders import Nominatim
import pandas as pd
import geoBaidu
import time
import coordTransform_utils  as geo_transform
geolocator = Nominatim()

df=pd.DataFrame(columns=['name','latitude','longitude','miss'])

raw_data=open(path+file_name,'r')


#location = geolocator.geocode("175 5th Avenue NYC")

#print(location.address)
#
#print((location.latitude, location.longitude))

    
Baidu=geoBaidu.geoBaidu(ak='DPlowD7PIEfaVtpxLKGkXg8yDCCBanVO')




i=0
for ele in raw_data:
#    location = geolocator.geocode(ele)
    location=Baidu.geocode([ele,'','北京','北京'])
    if location is None:
        df.loc[i,]=[ele,"","",0]
    else:
#        (lat,lgt)=geo_transform.bd09_to_wgs84(location.latitude,location.longitude)
        (lat,lgt)=geo_transform.bd09_to_gcj02(location.latitude,location.longitude)
        df.loc[i,]=[ele,lat,lgt,1]
    
    i=i+1
    time.sleep(0.5)



#output=Baidu.geocode([ele,'','北京','北京'])

df.to_csv(path+'gis_school.csv',sep=',',index=False)

#geo_transform.bd09_to_wgs84(df.ix[2,1],df.ix[2,2])