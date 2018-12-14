# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 12:43:06 2018

@author: xiaofeima
Data Clean
This script is aimed at cleaning the raw scrap data
Clean the bidding Data and get the highest bidding price for each bidder
 

"""



# package 
import sqlite3
import pandas as pd
import numpy as np
import time, re,copy
import matplotlib.pyplot as plt



store_path="E:/auction/"


# get the table name 
# auction_bidding auction_bidding_2 is the xuzhou bidding
# auction_bidding_house is other cities bidding info

con_bid = sqlite3.connect(store_path+"auction_bidding.sqlite")
cursor = con_bid.cursor()
tab_name=cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in tab_name:
    tab_name_list.append(name[0])
    

# ~ 
    
'''
clean the bidding data for each auction
get the each bidder's highest bidding price
get the bidding distance among the bidders

'''
col_name_bid=['ID','bidder_id','date','time','price','dist_high','position','status']
df_bid_info=pd.DataFrame(columns = col_name_bid )


flag=0
for name in   tab_name_list:
    df_Tab_temp = pd.read_sql_query("SELECT * from " + "'"+name+"'", con_bid)
    df_Tab_temp.drop(['index'],axis=1,inplace=True)
    df_Tab_temp['position']=df_Tab_temp.index
    temp_index=df_Tab_temp['position'].transform(lambda x: x[::-1])
    temp_index=temp_index.reset_index(drop=True)
    df_Tab_temp['position']=temp_index
    df_Tab_temp['ID']=name
    temp_group=df_Tab_temp.groupby('bidder_id')
    temp_max= temp_group.max()
    temp_max=temp_max.reset_index()
    length=df_Tab_temp.shape[0]
    temp_max['dist_high'] = (length-1) - temp_max['position']
    temp_max['ID'] = name
    temp_max=temp_max.loc[ :, col_name_bid]
    
    df_bid_info=df_bid_info.append(temp_max,ignore_index=True)
    
    
    
    if flag==0:
        DF_bid_table = df_Tab_temp.copy()
        
        flag=1
    else:
        
        
        DF_bid_table=DF_bid_table.append(df_Tab_temp)


con_bid_clean = sqlite3.connect(store_path+"bid_house_data.sqlite")
DF_bid_table.to_sql("xuzhou_2",con_bid_clean,if_exists="append")   

con_bid_clean2 = sqlite3.connect(store_path+"bid_house_info.sqlite")
df_bid_info.to_sql("xuzhou_2",con_bid_clean2,if_exists="append")   


## for other's bidding
col_name_bid=['ID','bidder_id','date','time','price','dist_high','position','status']
for name in  tab_name_list:
    df_bid_info=pd.DataFrame(columns = col_name_bid )
    flag=0

    df_Tab_temp = pd.read_sql_query("SELECT * from " + "'"+name+"'", con_bid)
    df_Tab_temp = df_Tab_temp.rename(columns={'ID_info': 'ID'})
    group_temp =  df_Tab_temp.groupby("ID")
    for ID in  group_temp.groups.keys():
        t_g_df = group_temp.get_group(ID).copy()
        t_g_df.drop(['index'],axis=1,inplace=True)
        t_g_df=t_g_df.reset_index(drop=True)
        t_g_df['position']=t_g_df.index
        temp_index=t_g_df['position'].transform(lambda x: x[::-1])
        temp_index=temp_index.reset_index(drop=True)
        t_g_df['position']=temp_index
        t_g_df['ID']=ID
        temp_group=t_g_df.groupby('bidder_id')
        temp_max= temp_group.max()
        temp_max=temp_max.reset_index()
        length=t_g_df.shape[0]
        temp_max['dist_high'] = (length-1) - temp_max['position']
        temp_max['ID'] = ID
        temp_max=temp_max.loc[ :, col_name_bid]
        df_bid_info=df_bid_info.append(temp_max,ignore_index=True)
    
        
        if flag==0:
            DF_bid_table = t_g_df.copy()
            
            flag=1
        else:
            
            DF_bid_table=DF_bid_table.append(t_g_df)
    
    con_bid_clean = sqlite3.connect(store_path+"bid_house_data.sqlite")
    DF_bid_table.to_sql(name,con_bid_clean,if_exists="replace")   

    con_bid_clean2 = sqlite3.connect(store_path+"bid_house_info.sqlite")
    df_bid_info.to_sql(name,con_bid_clean2,if_exists="replace")   



con_bid.close()
con_bid_clean.close()
con_bid_clean2.close()
