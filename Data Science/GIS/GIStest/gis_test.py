# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 11:00:50 2016
GIS test for python3 

baidu API interface

"""


import pandas as pd
from pandas import Series,DataFrame
import urllib
import hashlib
import requests
import math
import re
import json

pattern_x=re.compile(r'"x":(".+?")')
pattern_y=re.compile(r'"y":(".+?")')

# df = pd.read_csv('beijingsample.csv',sep=',')
 
# 以get请求为例http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak
queryStr = '/geocoder/v2/?address=北京市第二中学&city=北京市&output=json&ak=9gTAEoFWvBoKHl3u3dFp5ff7'
 
# 对queryStr进行转码，safe内的保留字符不转换
encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
 
# 在最后直接追加上yoursk
rawStr = encodedStr + 'DTtxldoesco94o9YZT3RuGlKarBGr7Xv'
temp_quote=urllib.parse.quote_plus(rawStr).encode('utf-8')
sn = hashlib.md5(temp_quote).hexdigest()

api_link = 'http://api.map.baidu.com'+queryStr+"&sn="+sn
 
# md5计算出的sn值7de5a22212ffaa9e326444c75a58f9a0
# 最终合法请求url是http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak&sn=7de5a22212ffaa9e326444c75a58f9a0
print(hashlib.md5(temp_quote).hexdigest())
print(api_link)
req = requests.get(api_link)
print(req)
print(req.content)
print(req.json())
content=req.json()
result = content[u'result']
location = result[u'location']
x = location[u'lat']
y = location[u'lng']
cofind=result[u'confidence']
level=result['level']
print(x,y,level,cofind)

df=pd.DataFrame(columns=['a','b','c','d'])

content=[(1,2,3,4),(5,6,7,8),(10,11,12,13)]


df.loc[0]=content[0]


fhandle=open('url2.txt','r')
url_content=fhandle.readlines()
fhandle.close()



def gis_extract(queryStr):
    encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
 
    # 在最后直接追加上yoursk
    rawStr = encodedStr + 'DTtxldoesco94o9YZT3RuGlKarBGr7Xv'
    temp_quote=urllib.parse.quote_plus(rawStr).encode('utf-8')
    sn = hashlib.md5(temp_quote).hexdigest()
    
    api_link = 'http://api.map.baidu.com'+queryStr+"&sn="+sn
     
    # md5计算出的sn值7de5a22212ffaa9e326444c75a58f9a0
    # 最终合法请求url是http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak&sn=7de5a22212ffaa9e326444c75a58f9a0
    print(hashlib.md5(temp_quote).hexdigest())
    print(api_link)
    req = requests.get(api_link)
    print(req)
    return req
#    print(req.content)
#    print(req.json())
#    content=req.json()
#    result = content[u'result']
#    location = result[u'location']
#    x = location[u'lat']
#    y = location[u'lng']
#    cofind=result[u'confidence']
#    level=result['level']
#    print(x,y,level,cofind)

gis_extract(url_content[1])
#sub_url_content=[]
#
#for i in range(0,len(url_content),10):
#    sub_url_content.append(url_content[i:i+10])
#sub_url_content[1]