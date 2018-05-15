# -*- coding: utf-8 -*-
"""
Created on Sun May  8 12:41:13 2016

@author: guoxuan

处理地理信息相关数据的转化

1. 行政区划名称-代码转换
"""
import pandas as pd
import numpy as np

#path="E:\\guoxuanma\\DATA\\compay_csv\\"
path='G:\\database\\company_geo\\'
path2='G:\\database\\company_geo_clean\\'
code_file_name="admin_code_2002-2014.csv"

##--------------------------------------------------------
# 行政区划 名称-代码转换
#
##--------------------------------------------------------



## read district data
def dist_convert(year):
    dict_name={
    '2000':[0,1],
    '2001':[0,1],    
    '2002':[0,1],
    '2003':[2,3],
    '2004':[4,5],
    '2005':[6,7],
    '2006':[8,9],
    '2007':[10,11],
    '2008':[12,13],
    '2009':[14,15],    
    
    }
    code_convert_df=pd.read_csv(path+code_file_name,encoding='gbk',header=0)
    code_convert_df.dropna(axis=0,how="all",inplace=True)
    code_cols=code_convert_df.columns
    
    
    ## get specific year code and name from 02 - 14 (10-12 is 2007) 
    
    convert_df=code_convert_df[code_cols[dict_name[year]]]
    convert_df.dropna(axis=0,how="all",inplace=True)
    convert_df.rename(columns={convert_df.columns[0]:"name",convert_df.columns[1]:"code"},inplace=True)
    convert_df['code']=convert_df['code'].astype(str)
    convert_df['code']=convert_df['code'].str[0:6]
    ## province 
    prov_flag=convert_df['code'].str.contains(r"\d{2}0000")
    prov_code=convert_df.loc[prov_flag,'code'].str[0:2]
    prov_name=convert_df.loc[prov_flag,'name']
    prov_df=pd.concat([prov_code,prov_name],axis=1)
    
    ## city
    city_flag=convert_df['code'].str.contains(r"\d{4}00")
    city_code=convert_df.loc[city_flag&(~prov_flag),'code'].str[0:4]
    city_name=convert_df.loc[city_flag&(~prov_flag),'name']
    city_df=pd.concat([city_code,city_name],axis=1)
    return convert_df, prov_df,city_df





###----------------------------------------------------------------------------
# clean the original data
# save the independent spatial or geographic data
###----------------------------------------------------------------------------

#temp=pd.read_stata(path+"2009.dta",encoding='gbk')
#cand_index=list(range(11))
#cand_index.append(64)
#geo_df=temp[temp.columns[cand_index]]

#geo_df.csv("E:\\2009t.csv",index=False,encoding='gbk')


data_names=['1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009']

#path2="E:\\guoxuanma\\DATA\\company_geo\\"
#path='E:\\guoxuanma\\DATA\\company2\\'


path="G:\\database\\company_geo\\"
path2="G:\\database\\company_geo_clean\\"

for name in data_names:
    
    convert_df, prov_df,city_df=dist_convert(name)
    #name='2000'
    temp=pd.read_table(path+name+".txt",encoding='utf-8',dtype=str,sep='\t')
    temp.fillna("",inplace=True)
    temp['street']=temp['street'].str.replace(".+办事处","")
    
    '''
    -------------------------------------------------------------------------------
    格式规整：
    对各个时间的工业企业数据库数据，统一规整为：
    1. 企业代码
    2. 企业名称
    3. 企业地址(乡镇、街道、号码)
    4. 区、县
    5. 城市
    6. 省份
    7. 省地县行政编码
    8. ID 号 
    -------------------------------------------------------------------------------
    '''
    
    ## name and ID
    
    temp_df=temp[['ID','firmID','firmName']].copy()
    
    ## total address
    
    temp_df['address']=temp['street']+""+temp['address']
    
    
    ## district Code and distrcit
    temp_df['districtCode']=temp['districtCode'].str[:6]
    #temp_df['districtCode2']=temp['districtCode'].str[6:]
    
    
    ##  利用merge 来进行省地县名称查找
    temp_df['pro_code']=temp_df['districtCode'].str[:2]
    temp_df['province']=pd.merge(temp_df[['ID','pro_code']],prov_df,left_on='pro_code',right_on='code',how='inner')['name']
    
    temp_df['city_code']=temp_df['districtCode'].str[:4]
    temp_df['city']=pd.merge(temp_df[['ID','city_code']],city_df,left_on='city_code',right_on='code',how='inner')['name']
    
    temp_df['county']=pd.merge(temp_df[['ID','districtCode']],convert_df,left_on='districtCode',right_on='code',how='inner')['name']
    
    temp_df.drop(axis=1,labels=['pro_code','city_code'],inplace=True)
    
    ## save the result
    
    temp_df.to_csv(path2+name+"_clean.txt",sep='\t',index=False,encoding='utf-8')
    



### database import 

import pandas as pd 
import os,glob
import sqlite3

path="G:\\database\\company_geo_clean\\"

## get all txt file in a dir
db_file=""
### method 1 
read_file_list =os.listdir(path)
file_list=[]
for file in read_file_list:
    if file.endswith(".txt"):
        file_list.append(file)
    if file.endswith(".db"):
        db_file=file
    
    
### method 2
read_file_list = glob.glob(path+'*.txt')
db_file=glob.glob(path+'*.db')
file_list=[x.split("\\")[-1] for x in read_file_list]

## current choose method 2 to use
conn = sqlite3.connect(db_file[0])
for i in range(3,12):
    temp=pd.read_csv(read_file_list[i],sep="\t",encoding="utf-8",dtype=str)
    table_name=file_list[i].split(".")[0]
    temp.to_sql(table_name, conn, if_exists='replace', index=False)






#-----------------------------------------------------------------------------
### 第一种解决办法 死慢无比
#temp_df.loc[:,'province']=temp.loc[:,'districtCode'].str[:2].apply(code2name)
#temp_df.loc[:,'city']=temp.loc[:,'districtCode'].str[:4].apply(code2name)
##temp_df.loc[temp_df['city'].str.contains('县级行政区'),'city']=""
#chunk=5000
#i=0
#n=len(temp)
#while i<=n:
#    if i+chunk>=n:
#        temp_end=n
#    else:
#        temp_end=i+chunk
#    temp_df.loc[:,'province']=temp.loc[:,'districtCode'].str[:2].apply(code2name)
#    temp_df.loc[:,'city']=temp.loc[:,'districtCode'].str[:4].apply(code2name)
#    temp_df.loc[i:temp_end,'district']=temp.loc[i:temp_end,'districtCode'].str[:6].apply(code2name)
#    i=temp_end+1
#    
#
#def code2name(code):
#    code=str(code)
#    try:    
#        if len(code)==2:
#            #province
#            name=prov_df.loc[prov_df['code']==code,'name']
#        elif len(code)==4:
#            if '90' in code:
#                name=''
#            else:
#                name=city_df.loc[city_df['code']==code,'name']
#        else:
#            name=convert_df.loc[convert_df['code']==code,'name']
#    except:
#        name=""
#    return name


'''
-------------------------------------------------------------------------------
test
-------------------------------------------------------------------------------
'''

import pandas as pd
import numpy as np
path="G:\\database\\company_geo\\"
path2="G:\\database\\company_geo_clean\\"
temp=pd.read_csv(path+"2007.txt",encoding='utf-8',dtype=str,)


## check nan 
#pd.isnull(temp.ix[1,2])
#np.isnan(temp.ix[1,2])

name_list=['2000','2001','2002','2003','2004','2005','2006']
name_list=['1996','1997','1998','1999','2000']
for i in name_list :
    try:
        temp=pd.read_csv(path+i+".txt",encoding='utf-8',dtype=str,sep='\t')
        print("--------------%s---------------" %i)        
        print(temp.head())
    except:
        print('error year '+i)
        
        