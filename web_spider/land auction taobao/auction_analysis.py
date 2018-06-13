# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 08:55:34 2018

@author: xiaofeima
auction data analysis 
detail info analysis
"""

import sqlite3
import pandas as pd
import time, re,copy


link_path="E:/auction/link/"

store_path="E:/auction/"



## connect to the sqlite
con = sqlite3.connect(store_path+"auction_info.sqlite")
con1 = sqlite3.connect(store_path+"auction_bidding_1.sqlite")
con2 = sqlite3.connect(store_path+"auction_bidding_2.sqlite")



# Load the data into a DataFrame
df_1 = pd.read_sql_query("SELECT * from xuzhou_1", con)
df_2 = pd.read_sql_query("SELECT * from xuzhou_2", con)


df_1['status2']=0
df_1.loc[df_1['status']=="done",'status2']=1
        
df_2['status2']=0
df_2.loc[df_2['status']=="done",'status2']=1
        
        
df_1['p_ratio']=df_1['win_bid']/df_1['eval_price']

df_2['p_ratio']=df_2['win_bid']/df_2['eval_price']



# Be sure to close the connection
con.close()
con2.close()