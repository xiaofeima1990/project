# -*- coding: utf-8 -*-
"""
Created on Fri May 20 22:53:44 2016

@author: xiaofeima

this file is aimed at running the gis geocoding loop to get GIS info from baidu

procedure
1. get the file name list
2. read the data 
3. reorganize the data 
4. running 

data format:
year_clean.txt

or sqlite database 


"""

import pandas as pd 
import numpy as np
import re,os 
import geoBaidu
import math,copy

'''
fucntion

'''
#path="E:\\guoxuanma\\gis\\first-land-market\\"
#path2="E:\\guoxuanma\\gis\\first-land-market-gis\\"
#
#path_dist="E:\\guoxuanma\\gis\\district-info\\"
#

# get file name list function 
def datafile_cate(path):
    savefile=[]
    read_file_list =os.listdir(path)
    
    for element in read_file_list:
        savefile.append(os.path.splitext(os.path.basename(element)))
    
    # year=savefile[1][0].split('-')
    # year[0]
    f_year=set()
    temp_list=[]
    f_name_cat={}
    for ele in savefile:
    #     print(ele)
        year=ele[0].split('-')[0]
        f_year.add(year)
    # f_year
    # temp_list
    for ele in f_year:
        for ele2 in savefile:
            if ele in ele2[0]:
                temp_list.append(ele2[0]+ele2[1])    
        f_name_cat[ele]=copy.copy(temp_list)
        temp_list=[]
    
    return f_name_cat

## assign the distrct name (not used in industry company gis ) 
def df_dist_get(year,path=path_dist):
    raw_dist=pd.read_csv(path+year+'.csv',encoding='gbk')
    for x in raw_dist.columns:
        raw_dist[x]=raw_dist[x].astype(str)
    ## province 
    prov_flag=raw_dist['code'].str.contains(r"\d{2}0000")
    prov_code=raw_dist.loc[prov_flag,'code'].str[0:2]
    prov_name=raw_dist.loc[prov_flag,'name']
    prov_df=pd.concat([prov_code,prov_name],axis=1)
    
    ## city 
    
    city_flag=raw_dist['code'].str.contains(r"\d{4}00")
    city_code=raw_dist.loc[city_flag&(~prov_flag),'code'].str[0:4]
    city_name=raw_dist.loc[city_flag&(~prov_flag),'name']
    city_df=pd.concat([city_code,city_name],axis=1)
    
    ## county 
    county_code=raw_dist.loc[~(city_flag|prov_flag),'code']
    county_name=raw_dist.loc[~(city_flag|prov_flag),'name']
    county_df=pd.concat([county_code,county_name],axis=1)
    
    return (prov_df,city_df,county_df)

    

 
## gecoding function 
def get_geocoding(df):
    '''
    first try firm name to locate
    then try the address
    
    '''
    id_index=df['ID']
    new_ID=df['new_ID']
    name=df['firmName']
    query=df[['firmName','county','city','province']]
    county=df['county']
    
    try: 
        output=Baidu.geocode(query)
        [lat,lng]=output.latlng
        confidence=output.confidence
    except Exception as e:
#        print('no info ')
        try:
            query=df[['address','county','city','province']]
            output=Baidu.geocode(query)
            [lat,lng]=output.latlng
            confidence=output.confidence
        except:
            
            (id_index,new_ID,name,lat,lng,confidence,county)=(id_index,new_ID,name,"","","",county)
        
    return (id_index,new_ID,name,lat,lng,confidence,county)
    

## 缺少代码和行政区划名称转化
## df_dist_prov, df_dist_city, df_dist_county
#def district_name(ID_code,prov_df,city_df,county_df):
#    code=str(ID_code)[:6]
#    province=''
#    city=''
#    county=''
#    
#    try:
#        province=prov_df.loc[code[:2],'name']  
#    except Exception as e:
#        province=''
#  
#    if '00' not in code[2:4]:
#        try:
#            city=city_df.loc[code[:4],'name']
#        except Exception as e:
#            city=''
#
#
#    if '00' not in code[4:6]:
#        try:
#            county=county_df.loc[code,'name']
#        except Exception as e:
#            county=''
#    
#    
#    return (province,city,county)


def new_ID(i,fname):
    ID_date=''.join(re.findall('\d+',fname))
#    ID_district=ID[:6]
    ID_n=''.join([ID_date,str(i)])
    return ID_n



#read_file_list =os.listdir(path)

#data_fname=input("please input the test data file name (2015-01.csv)")


# test for gis info geocoding
# geo_info=Baidu.geocode(data_geoInfo.loc[2,['address','county','city','province']].tolist())



def get_gis_info(data_fname,data_raw,path2):
    
    geo_info=pd.DataFrame(columns=['ID','new_ID','firmName','lat','lng','confidence','county'])
    empty_count=0
    for i in data_raw.index:
        geo_info.loc[i,]=get_geocoding(data_raw.loc[i,:])
        if geo_info.loc[i,'lat']=='':
            empty_count+=1

        if i % 10000 ==0 || i==data_raw.index[-1]:

            print('until %s , %s empty gis has %d' %(str(i),data_fname,empty_count))
            
            total_df=pd.merge(geo_info,data_raw,on='new_ID',how='inner')
            if not os.path.isfile("gis-"+data_fname):
                geo_info.to_csv(path2+"gis-"+data_fname,index=False,sep='\t',mode='w',header=True)
                total_df.to_csv(path2+"total-"+data_fname,index=False,sep='\t',mode='w',header=True)
            else:
                geo_info.to_csv(path2+"gis-"+data_fname,index=False,sep='\t',mode='a',header=False)
                total_df.to_csv(path2+"total-"+data_fname,index=False,sep='\t',mode='a',header=False)



            geo_info=pd.DataFrame(columns=['ID','new_ID','firmName','lat','lng','confidence','county'])
    print('complete the %s geocoding' %data_fname)
    print('--------------------------------------')
#    temp_procedure=math.floor(i/(int(len(data_geoInfo)*percent))*100)
#    if temp_procedure%5==0:
#        print("finished "+ str(temp_procedure)+"% total data")
    

if __name__ == '__main__':


    '''
    RUN THE GEOCODING
    '''
    
    path=input('please enter the source data path')
    path2=input("please enter the organized data path ")
    
    ## 获取地理位置信息
    Baidu=geoBaidu.geoBaidu(ak='DPlowD7PIEfaVtpxLKGkXg8yDCCBanVO')
    
    year=input('please input the year for geocoding')
    cat_list=datafile_cate(path)
    file_list=cat_list[year]
    
    #(prov_df,city_df,county_df)=df_dist_get(year,path_dist)
    
    for data_fname in file_list:
        print('strating the %s gecoding' %data_fname)    
        data_raw=pd.read_csv(path+data_fname,sep='\t',encoding='utf-8',dtype=str)
    #    data_raw.reset_index(inplace=True)
        data_raw['i']=data_raw.index
        data_raw['new_ID']=data_raw['i'].apply(lambda x : new_ID(x,data_fname))
        data_raw.drop(labels=['i'],axis=1,inplace=True)
        get_gis_info(data_fname,data_raw,path2)
        






'''
appendix

'''
#
#raw_dist=pd.read_csv(path_dist+year+'.csv',encoding='gbk')
#for x in raw_dist.columns:
#    raw_dist[x]=raw_dist[x].astype(str)
#    raw_dist[x]=raw_dist[x].str.strip("?")
#raw_dist.to_csv(path_dist+year+'n.csv',index=False)
