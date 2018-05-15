# -*- coding: utf-8 -*-
"""
Created on Tue May 10 20:28:56 2016

@author: guoxuan

This file is aimed at dealing with all the data cleaning and manuipulating

this script include

1. get the grouped data file list
2. merge small pieceful data into a large data
3. select info columns from data file 



env python 3.4
"""
import pandas as pd
import numpy as np
import copy
import os


## ----------------------------------------------------
## 分列
## ----------------------------------------------------
#col=data2.columns[0]
#data_new=data2[col].str[1:-1].str.split(',', return_type='frame')
#data_new.drop(labels=data_new.columns[-1],axis=1,inplace=True)
#
#
#cols=col.split(',')
#old_cols=data_new.columns.tolist()
#new_cols=['address','region_code','id','province','city','county']
#data_new.rename(columns=dict(zip(old_cols, new_cols)), inplace=True)
#




class Data_Analysis:
    def __init__(self,path,filename_address,filename_prov,district_info_path):
        self.path=path
        self.filename_address=filename_address
        self.filename_prov=filename_prov
        self.district_info_path=district_info_path
        flag1=_get_code_name_info(self)
        
        
    def datafile_cate(self):
        savefile=[]
        read_file_list =os.listdir(self.path)
        
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

    def merge_data(self,year,f_name_cat):
        
        file_list=f_name_cat[year]
        count=0
        try:
            for file_ele in file_list:
        
                temp_data_df = pd.read_excel(self.path+file_ele)
                print(temp_data_df.shape)
                ######
                # mege data
                ######
                if count==0:
                    data_df=temp_data_df
                else:
                    data_df=data_df.append(temp_data_df,ignore_index=True)
        
                count+=1
                
        except Exception as e:
            print('error: ',e)
            return False
        return data_df 
        


    def select_columns(self, cols_name,new_cols_name):
        
        pass
    
    
    def code2name(self, data_df,code_col,district_level='province'):
        data_df[code_col]=data_df[code_col].astype(str)
        if district_level=='province':
            refer_df=self.prov_df
            code_df=data_df[code_col].str[0:2]
        elif district_level=='city':
            refer_df=self.city_df
            code_df=data_df[code_col].str[0:4]
        else:
            refer_df=self.county_df
            code_df=data_df[code_col].str[0:6]
        

        name_df=code_df.apply(lambda x : refer_df.ix[refer_df['code']==x,1])
        return name_df
        
    def _get_code_name_info(self):
                
        ## construct the province city county address index
        prov=pd.read_csv(self.district_info_path + self.filename_prov,sep='\t',header=0)
        prov.rename(columns={prov.columns[0]:"province"},inplace=True)
        prov['code']=prov['code'].astype(str)
        prov2code_dict=dict(zip(prov['province'],prov['code']))
        code2prov_dict=dict(zip(prov['code'],prov['province']))
        
        
        ## construct the province city county address index
        address=pd.read_csv(self.district_info_path+self.filename_address,sep='\t',header=0)
        address.rename(columns={address.columns[0]:"code"},inplace=True)
        address['county']=address['county'].str.strip()
        address['code']=address['code'].astype(str)
        
        
        
        ## province
        prov_flag=address['code'].str.contains(r"\d{2}0000")
        prov_code=address.loc[prov_flag,'code'].str[0:2]
        prov_name=address.loc[prov_flag,'county']
        prov_df=pd.concat([prov_code,prov_name],axis=1)
        
        
        city_flag=address['code'].str.contains(r"\d{4}00")
        city_code=address.loc[city_flag&(~prov_flag),'code'].str[0:4]
        city_name=address.loc[city_flag&(~prov_flag),'county']
        city_df=pd.concat([city_code,city_name],axis=1)
        
        county_flag=address['code'].str.contains(r"\d{6}")
        county_code=address.loc[county_flag&(~prov_flag),'code'].str[0:4]
        county_name=address.loc[county_flag&(~prov_flag),'county']
        county_df=pd.concat([county_code,county_name],axis=1)
        
        
        self.prov_df=prov_df
        self.city_df=city_df
        self.county_df=county_df
        
        
        if len(prov_df)>0 and len(city_df)>0 and (county_df)>0:
            return 1
        else:
            print('error: can not get code and district name info correctly')
            return 0
