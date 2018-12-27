#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 00:23:47 2018

@author: xiaofeima
used for data preparation 
organized as :
    1. activity
    2. last state 
    3. basic information
    4. winning bid 

"""

# package 
import sqlite3
import pandas as pd
import numpy as np
import time, re,copy
import matplotlib.pyplot as plt
import pandas as pd

store_path="/Users/xiaofeima/Documents/auction/"

from collections import defaultdict,OrderedDict

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() 
                            if len(locs)>0)
    

# bidding info 1 
con_bid_clean = sqlite3.connect(store_path+"bid_house_data.sqlite")
### list table names 
res = con_bid_clean.execute("SELECT name FROM sqlite_master WHERE type='table';")
flag=0
for name in res:
    print(name[0])

    if flag==0:
        df_bid_1 = pd.read_sql_query("SELECT * from "+name[0], con_bid_clean)
    else:
        df_bid_1.append(pd.read_sql_query("SELECT * from "+name[0], con_bid_clean),ignore_index=True,inplace=True)

# auction info 1
con_bid_clean = sqlite3.connect(store_path+"auction_info_house.sqlite")
res = con_bid_clean.execute("SELECT name FROM sqlite_master WHERE type='table';")
flag=0
for name in res:
    print(name[0])
    if flag==0:
        df_auction_1=pd.read_sql_query("SELECT * from "+name[0], con_auction_clean)
    else:
        df_auction_1.append(pd.read_sql_query("SELECT * from "+name[0], con_auction_clean),ignore_index=True,inplace=True)

# column_name = ['status', 'bidder_id', 'price', 'date', 'time', 'position', 'ID']]

 

# get the bid activity : 
group_df1=df_bid_1.groupby('ID')


ID_index='40133084923'
temp_df=group_df1.get_group(ID_index)
temp_df=temp_df.sort_index(ascending=False)
bidder_act= temp_df['bidder_id'].tolist()
# get the player bidding activity  
bidder_pos=list(list_duplicates(bidder_act))


# get the last state for each bidder: 
bidder_state=[]
for ele in x: 
	bidder_state.append(ele[1][-1])

# I think I can make the bid_info into a big dataframe 

bid_info={
	'ID',ID_index,
	'bidder_act',bidder_act,
	'bidder_pos',bidder_pos,
	'bidder_state',bidder_state,

}


# get the auction information 

info_name=['evaluation_prce','reserve_price','ladder','ID','year','location','lgt','lat','win_price','num_bidder'.'priority_bidder']
