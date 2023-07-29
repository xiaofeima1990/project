# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 17:16:17 2021

@author: guoxuan

Pure HHI calculation from sod 


"""

import pandas as pd
import numpy as np
import time, re,copy
import matplotlib.pyplot as plt
import os
from pandas.api.types import is_string_dtype


path_sod = "D:/Dropbox/academic/11_work_dataset/firm dynamics and growth/macro_IV/raw_data/bank_SOD/"
path = "D:/Dropbox/academic/11_work_dataset/firm dynamics and growth/rate-watch/"
path_cross_walk = "D:/Dropbox/academic/12_database/GEO_crosswalk/clean/"
flag_0 = 0 



GEO_CODE = "MSA"


def SOD_HHI(path_sod,GEO_CODE = "MSA"):
    df_bank_SOD= pd.read_csv(path_sod+ "bank_SOD_03_11.zip", sep = "\t")
    Col_names = ['CERT','YEAR','BRNUM','NAMEFULL','NAMEBR','BRSERTYP','RSSDID','STALPBR',
                 'ZIPBR','MSABR','MICROBR','CNTYNUMB','STCNTYBR','CITY2BR','CITYBR',
                 'ASSET','DEPDOM','DEPSUM','DEPSUMBR']
    
    fin_cols = ['ASSET','DEPDOM','DEPSUM','DEPSUMBR']
    df_bank_prep = df_bank_SOD[Col_names]
    
    ### clean the data
    for ele in fin_cols:
        type_flag = is_string_dtype(df_bank_prep[ele])
        if type_flag:
            df_bank_prep[ele] = df_bank_prep[ele].astype(str)
            df_bank_prep[ele] = df_bank_prep[ele].str.replace(",","")
            df_bank_prep[ele] = df_bank_prep[ele].astype(float)
            
    
    ### aggregate 
    df_bank_HHI = df_bank_prep.groupby(["YEAR","MSABR","CERT"]).agg({'NAMEBR':'count','ASSET':'max','DEPDOM':'max','DEPSUMBR':'sum'})
    
    df_bank_HHI = df_bank_HHI.reset_index()
    df_bank_HHI = df_bank_HHI.rename(columns = {"NAMEBR":"NUMBR","MSABR":GEO_CODE})
    
    # get the region HHI 
    temp_df_group = df_bank_HHI.groupby(['YEAR',GEO_CODE]).agg({"DEPSUMBR":"sum",'NUMBR':'sum'})
    temp_df_group.columns=['DEPSUMBR_SUM','NUMBR_SUM']
    temp_df_group= temp_df_group.reset_index()
    df_bank_HHI = df_bank_HHI.merge(temp_df_group,on = ['YEAR',GEO_CODE],how = "left")
    df_bank_HHI['mkt_share'] = df_bank_HHI['DEPSUMBR']/df_bank_HHI['DEPSUMBR_SUM']
    
    df_bank_HHI['mkt_share2'] = (df_bank_HHI['mkt_share']*100)**2
    temp_df_group = df_bank_HHI.groupby(['YEAR',GEO_CODE]).agg({"mkt_share2":"sum"})
    temp_df_group.columns=['HHI']
    temp_df_group= temp_df_group.reset_index()
    df_bank_HHI = df_bank_HHI.merge(temp_df_group,on = ['YEAR',GEO_CODE],how = "left")
    
    
    return df_bank_HHI


df_bank_HHI = SOD_HHI(path_sod,GEO_CODE)