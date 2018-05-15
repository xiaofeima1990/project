# -*- coding: utf-8 -*-
"""
Created on Sat May  7 14:18:45 2016

@author: guoxuan
"""

import geopy
from geopy.distance import *

import requests
from urllib.parse import *
import math
import re
import json

ak='DPlowD7PIEfaVtpxLKGkXg8yDCCBanVO'

DEFAULT_HEADERS={
'Content-Type': 'text/javascript;charset=utf-8', 
'Cache-Control': 'max-age=86400', 
'Http_x_bd_logid': '111371565', 
'Content-Length': '117', 
'Server': 'Apache', 
'Http_x_bd_product': 'map', 
'Http_x_bd_subsys': 'apimap', 
'Set-Cookie': 'BAIDUID=C0DB927F7CB019F363EE59AB98707659:FG=1; max-age=31536000; expires=Tue, 11-Apr-17 02:45:35 GMT; domain=.baidu.com; path=/; version=1, BAIDUID=CE92432093552CE88CF5E36575C752B5:FG=1; expires=Tue, 11-Apr-17 02:45:35 GMT; max-age=31536000; path=/; domain=.baidu.com; version=1', 
'Date': 'Mon, 11 Apr 2016 02:45:35 GMT', 
'Expires': 'Tue, 12 Apr 2016 02:45:35 GMT', 
'Content-Encoding': 'gzip', 
'Http_x_bd_logid64': '11754213925618355716', 
'P3p': 'CP=" OTI DSP COR IVA OUR IND COM ", CP=" OTI DSP COR IVA OUR IND COM "'
}
USER_AGENT='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'


# Average great-circle radius in kilometers, from Wikipedia.
# Using a sphere with this radius results in an error of up to about 0.5%.
EARTH_RADIUS = 6372.795


# From http://www.movable-type.co.uk/scripts/LatLongVincenty.html:
#   The most accurate and widely used globally-applicable model for the earth
#   ellipsoid is WGS-84, used in this script. Other ellipsoids offering a
#   better fit to the local geoid include Airy (1830) in the UK, International
#   1924 in much of Europe, Clarke (1880) in Africa, and GRS-67 in South
#   America. America (NAD83) and Australia (GDA) use GRS-80, functionally
#   equivalent to the WGS-84 ellipsoid.
ELLIPSOIDS = {
    # model           major (km)   minor (km)     flattening
    'WGS-84':        (6378.137, 6356.7523142, 1 / 298.257223563),
    'GRS-80':        (6378.137, 6356.7523141, 1 / 298.257222101),
    'Airy (1830)':   (6377.563396, 6356.256909, 1 / 299.3249646),
    'Intl 1924':     (6378.388, 6356.911946, 1 / 297.0),
    'Clarke (1880)': (6378.249145, 6356.51486955, 1 / 293.465),
    'GRS-67':        (6378.1600, 6356.774719, 1 / 298.25)
}





class geoBaidu():
    
    def __init__(self,ak,output='json',user_agent=USER_AGENT,proxies=None,timeout=2,radius='2000'):
        
        self._ak=ak
        self._output=output
        self._geopy_baidu=geopy.geocoders.Baidu(self._ak)
        self._base_geocoding_url='http://api.map.baidu.com/geocoder/v2/'
        self._base_revgeocoding_url='http://api.map.baidu.com/place/v2/search'
        self._proxies = proxies
        self._timeout = timeout
        self._headers =  user_agent
        self._radius=radius
#        self.dic_list={
#            'ak':self.ak,
#            'output':self.output,
#            #'callback':callback, 不能加！ 否则 json 有问题
#            'address':'',
#            'city':'',
#            'district':'',
#            'province':'',
#            }
#        self.dic_list_rev={
#                'ak':self.ak,
#                'output':self.output,
#                #'callback':callback, 不能加！ 否则 json 有问题
#                'location':"",
#                'query':'',
#                'radius':self.radius,
#                }
#                
    @property
    def radius(self):
        return self._radius
        
    @radius.setter
    def set_radius(self, radius='2000'):
        
        self._radius=radius
        
        
    def geocode(self, query,timeout=2,pandas_flag=0):
        '''
        input parameter: 
        
        query(list) is the seraching address information and has the following sequence 
        ['title','address','disctrict','city','province']
        if query is in pandas.DataFrame format, then column_names is 
        ['title','address','disctrict','city','province']
        if city is empty, then left the element empty in either list or DataFrame
        
        pandas_flag is the flag for check whether it is DataFrame or not 
        
        '''
        
        params = {
            'ak': self._ak,
            'output': self._output,
            'address':'',
            'city':'',
            'district':'',
            'province':'',
        }
        
        if pandas_flag==0:
            # single input
            
            params['address'],params['disctrict'],params['city'],params['province']=query
            api_link="?".join((self._base_geocoding_url, urlencode(params)))


        else:
            ## multipul input
            pass
        
        return self._parse_json(
            self._call_geocoder(api_link),params['address']
        )
        
    
    def location_surround(self, location,query='', timeout=None,tag='',scope='2',):  # pylint: disable=W0221
        
        """
        Given a point, find an address.

        :param location: The coordinates for which you wish to obtain the
            closest human-readable addresses.
        :type location: :class:`geopy.point.Point`, list or tuple of (latitude,
            longitude), or string as "%(latitude)s, %(longitude)s"
        
        :param str query: the intended information you wish to find , such as bank, station,酒店，商场 etc.
        :type query : must be str, support multiple keywords, can be a list or tuple
        : eg: ('银行','饭店')
        :seperated by $, such as 酒店$银行$餐厅
        
        :param int timeout: Time, in seconds, to wait for the geocoding service
            
        :param str radius: the radius that you wish to search in a circle 
        
        :param str tag: the poi tag to specify can be multiple seperated by , 
        ：eg ('星级酒店','快捷酒店','公寓式酒店')
        :see http://lbsyun.baidu.com/index.php?title=lbscloud/poitags for classification
        
        :param str scope indicate whether the return infor is in detail or not 
        : default is 2. 1 is not detail 2 is detail (detail information knows distance and more infor)
        
        more information can be see in http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi
        """
        
        
        params = {
            'ak': self._ak,
            'output': self._output,
            'location': ','.join(str(x) for x in location),
            'query':'$'.join(str(x) for x in query),
            'radius':self._radius,
            'tag':','.join(str(x) for x in tag),
            'scope':'2',
        }

        api_link = "?".join((self._base_revgeocoding_url, urlencode(params)))  
        
        return self._parse_surround_json(
            self._call_geocoder(api_link)
        )
    
    
    @staticmethod
    def _parse_json(page,address=''):
        """
        Parses a location from a single-result reverse API call.
        """
        place = page['result']
        if not place:
            return None
            
        confidence=place['confidence']
        latitude = place['location']['lat']
        longitude = place['location']['lng']
        
        location_dict={
        'address':address,
        'lat':latitude,
        'lng':longitude,
        
        'confidence':confidence,
        'name':'',
        'info_tag':'',
        'info_type':'',
        'distance':'',
        
        
        }

        return Location(location_dict)
    
    def _parse_surround_json(self, page, closest=False):
        """
        Returns location, (latitude, longitude) from JSON feed.
        
        """

        place = page['results']

        if not place:
            return None

        def parse_place(place):
            """
            reorganize the data 
            """
            df=pd.DataFrame(place)
            df_final=pd.DataFrame(df.index)
            print('在方圆 %s 范围内：共找到 %s 个 符合条件的信息' %(self._radius,len(df)))
#            print(df)
            if len(df_final)>0:
                df_detail=pd.DataFrame(x for x in df['detail_info'])
                df_location=pd.DataFrame(x for x in df['location'])
            print(len(df_detail))
            df_final[['address','name']]=df[['address','name']]
            print(df_location)
            df_final[['lat','lng']]=df_location[['lat','lng']]
            df_final[['distance','tag','type']]=df_detail[['distance','tag','type']]
            
            df_final.sort('distance',ascending=True,inplace =True)
            
            return df_final
            
        df_location=parse_place(place)

        if closest:
            location_dict=df_location.loc[0,:].to_dict()
            location_dict['confidence']=''
            
            return Location(location_dict)
        else:
            location_list=[]
            for i in range(len(df_location)):
                location_dict=df_location.loc[i,:].to_dict()
                location_dict['confidence']=''
                location_list.append(location_dict.copy())
            return [Location(item) for item in location_list]
    
    
    
    
    
    def _call_geocoder(            
            self,
            url,
            ):
        s = requests.Session()
        s.headers['User-Agent']=self._headers
        
        try:
            page=s.get(url,timeout=self._timeout).json()
        except Exception as error:
            if isinstance(error, HTTPError):
                raise error
            elif isinstance(error, URLError):
                if "timed out" in message:
                    raise 'Service timed out'
                elif "unreachable" in message:
                    raise 'Service not available'
            elif isinstance(error, SocketTimeout):
                raise 'Service timed out'
            elif isinstance(error, SSLError):
                if "timed out" in message:
                    raise 'Service timed out'
        
        return page

    '''
    Calculate the distance between different GIS location
    计算经纬度之间的距离
    来自geopy里面
    
    '''
      
    def Dis_vinc(self,gis_p1,gis_p2,_ellipsoid='WGS-84'):
        '''
        
        Here's an example usage of distance.vincenty::
        
            >>> from geopy.distance import vincenty
            >>> newport_ri = (41.49008, -71.312796)
            >>> cleveland_oh = (41.499498, -81.695391)
            >>> print(vincenty(newport_ri, cleveland_oh).miles)
            538.3904451566326
        
        Using great-circle distance::
        
            >>> from geopy.distance import great_circle
            >>> newport_ri = (41.49008, -71.312796)
            >>> cleveland_oh = (41.499498, -81.695391)
            >>> print(great_circle(newport_ri, cleveland_oh).miles)
            537.1485284062816
        
        You can change the ellipsoid model used by the Vincenty formula like so::
        
            >>> distance.vincenty(ne, cl, ellipsoid='GRS-80').miles

        
        ''' 
        if _ellipsoid=='WGS-84':
            temp_measure=vincenty(gis_p1, gis_p2)
#            dis_kilometers=vincenty(gis_p1, gis_p2).kilometers
            
        else:
            temp_measure=vincenty(gis_p1, gis_p2,_ellipsoid=ellipsoid)
#            dis_kilometers=vincenty(gis_p1, gis_p2).kilometers
        
        distance_dict={
            'miles':       temp_measure.miles, 
            'kilometers':  temp_measure.kilometers,
            'meters':      temp_measure.meters,
            'feet':        temp_measure.feet,
        
        }
            
        
        return Dis_result(distance_dict)



class Dis_result(object):
    def __init__(self,distance_dict):
        '''
        mesure the distance include
        1. miles
        2. kilometers
        3. meters
        4. feet
        distance_measure={
          'miles':, 
          'kilometers':,
          'meters':,
          'feet',
        
        }
        
        '''
        self.distance_dict=distance_dict
    @property 
    def miles(self):
        '''
        return miles
        '''
        return self.distance_dict['miles']

    @property 
    def meters(self):
        '''
        return miles
        '''
        return self.distance_dict['meters']
        
    @property 
    def kilometers(self):
        '''
        return miles
        '''
        return self.distance_dict['kilometers']
        
    @property 
    def feet(self):
        '''
        return miles
        '''
        return self.distance_dict['feet']







### return the location class 
class Location(object):
    def __init__(self,location_dict):
        '''        
        location_dict={
            'address':address,
            'name':name,
            'lat':lat,
            'lng':lng,
            'distance':distance,
            'info_tag':info_tag,
            'info_type':info_type,
            'confidence':confidence
            'distance':distance,
            }
            '''
        
        self._location_dict=location_dict

    @property 
    def address(self):
        """
        Location as a formatted string returned by the geocoder or constructed
        by geopy, depending on the service.

        :rtype: unicode
        """
        return self._location_dict['address']

    @property
    def latitude(self):
        """
        Location's latitude.

        :rtype: float or None
        """
        return self._location_dict['lat']

    @property
    def longitude(self):
        """
        Location's longitude.

        :rtype: float or None
        """
        return self._location_dict['lng']
        
    @property
    def latlng(self):

        return (self._location_dict['lat'],self._location_dict['lng']) if self._location_dict['lng'] != None else None

    @property
    def confidence(self):
        """
        Location's confidence.

        :rtype: float or None
        """
        return self._location_dict['confidence']
        
    @property
    def distance(self):
        """
        Location's confidence.

        :rtype: float or None
        """
        return self._location_dict['distance']
    
    @property 
    def tag(self):
        """
        银行 美食

        :rtype: unicode
        """
        return self._location_dict['info_tag']

    @property 
    def type(self):
        """
        type as bank

        :rtype: unicode
        """
        return self._location_dict['info_type']
        
        
'''
Calculate the distance between different GIS location
计算经纬度之间的距离
来自geopy里面

[Vincenty distance](https://en.wikipedia.org/wiki/Vincenty's_formulae) or
[great-circle distance](https://en.wikipedia.org/wiki/Great-circle_distance)
formulas, with a default of Vincenty available as the function
`geopy.distance.distance`.

Vincenty distance (:class:`.vincenty`) uses a more accurate ellipsoidal model
of the earth. This is the default distance formula, and is thus aliased as
``distance.distance``. There are multiple popular ellipsoidal models, and
which one will be the most accurate depends on where your points are located
on the earth. The default is the WGS-84 ellipsoid, which is the most globally
accurate. geopy includes a few other
models in the distance.ELLIPSOIDS dictionary::

                  model             major (km)   minor (km)     flattening
    ELLIPSOIDS = {'WGS-84':        (6378.137,    6356.7523142,  1 / \
                                                                298.257223563),
                  'GRS-80':        (6378.137,    6356.7523141,  1 / \
                                                                298.257222101),
                  'Airy (1830)':   (6377.563396, 6356.256909,   1 / \
                                                                299.3249646),
                  'Intl 1924':     (6378.388,    6356.911946,   1 / 297.0),
                  'Clarke (1880)': (6378.249145, 6356.51486955, 1 / 293.465),
                  'GRS-67':        (6378.1600,   6356.774719,   1 / 298.25),
                  }

Here's an example usage of distance.vincenty::

    >>> from geopy.distance import vincenty
    >>> newport_ri = (41.49008, -71.312796)
    >>> cleveland_oh = (41.499498, -81.695391)
    >>> print(vincenty(newport_ri, cleveland_oh).miles)
    538.3904451566326

Using great-circle distance::

    >>> from geopy.distance import great_circle
    >>> newport_ri = (41.49008, -71.312796)
    >>> cleveland_oh = (41.499498, -81.695391)
    >>> print(great_circle(newport_ri, cleveland_oh).miles)
    537.1485284062816

You can change the ellipsoid model used by the Vincenty formula like so::

    >>> distance.vincenty(ne, cl, ellipsoid='GRS-80').miles

The above model name will automatically be retrieved from the
ELLIPSOIDS dictionary. Alternatively, you can specify the model values
directly::

    >>> distance.vincenty(ne, cl, ellipsoid=(6377., 6356., 1 / 297.)).miles

Distances support simple arithmetic, making it easy to do things like
calculate the length of a path::

    >>> d = distance.distance
    >>> _, wa = g.geocode('Washington, DC')
    >>> _, pa = g.geocode('Palo Alto, CA')
    >>> print((d(ne, cl) + d(cl, wa) + d(wa, pa)).miles)
    3276.157156868931



'''


'''
simply cite geopy to get the distance 

'''


    



'''
poi tag 

美食	中餐厅、外国餐厅、小吃快餐店、蛋糕甜品店、咖啡厅、茶座、酒吧
酒店	星级酒店、快捷酒店、公寓式酒店
购物	购物中心、超市、便利店、家居建材、家电数码、商铺、集市
生活服务	通讯营业厅、邮局、物流公司、售票处、洗衣店、图文快印店、照相馆、房产中介机构、公用事业、维修点、家政服务、殡葬服务、彩票销售点、宠物服务、报刊亭、公共厕所
丽人	美容、美发、美甲、美体
旅游景点	公园、动物园、植物园、游乐园、博物馆、水族馆、海滨浴场、文物古迹、教堂、风景区
休闲娱乐	度假村、农家院、电影院、KTV、剧院、歌舞厅、网吧、游戏场所、洗浴按摩、休闲广场
运动健身	体育场馆、极限运动场所、健身中心
教育培训	高等院校、中学、小学、幼儿园、成人教育、亲子教育、特殊教育学校、留学中介机构、科研机构、培训机构、图书馆、科技馆
文化传媒	新闻出版、广播电视、艺术团体、美术馆、展览馆、文化宫
医疗	综合医院、专科医院、诊所、药店、体检机构、疗养院、急救中心、疾控中心
汽车服务	汽车销售、汽车维修、汽车美容、汽车配件、汽车租赁、汽车检测场
交通设施	飞机场、火车站、地铁站、长途汽车站、公交车站、港口、停车场、加油加气站、服务区、收费站、桥
金融	银行、ATM、信用社、投资理财、典当行
房地产	写字楼、住宅区、宿舍
公司企业	公司、园区、农林园艺、厂矿
政府机构	中央机构、各级政府、行政单位、公检法机构、涉外机构、党派团体、福利机构、政治教育机构

'''