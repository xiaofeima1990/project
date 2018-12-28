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

#store_path="/Users/xiaofeima/Documents/auction/"

store_path ='G:/auction/clean/'

from collections import defaultdict,OrderedDict

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() 
                            if len(locs)>0)
    

'''
-------------------------------------------------------------------------------
data loading
-------------------------------------------------------------------------------
'''
# load bidding info 1 
con_bid_clean = sqlite3.connect(store_path+"bid_house_data.sqlite")
### list table names 
res = con_bid_clean.execute("SELECT name FROM sqlite_master WHERE type='table';")
flag=0
for name in res:
    print(name[0])

    if flag==0:
        df_bid_1 = pd.read_sql_query("SELECT * from "+name[0], con_bid_clean)
        flag=1
    else:
        df_bid_1=df_bid_1.append(pd.read_sql_query("SELECT * from "+name[0], con_bid_clean),ignore_index=True)

'''
-------------------------------------------------------------------------------
'''
# load auction info 1
con_auction_clean = sqlite3.connect(store_path+"auction_info_house.sqlite")
res = con_auction_clean.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in res:
    if "1" in name[0]:
        tab_name_list.append(name[0])
flag=0
for name in tab_name_list:
    print(name)
    if flag==0:
        df_auction_1=pd.read_sql_query("SELECT * from "+name, con_auction_clean)
        flag=1
    else:
        df_auction_1=df_auction_1.append(pd.read_sql_query("SELECT * from "+name, con_auction_clean),ignore_index=True)

'''
-------------------------------------------------------------------------------
get the bid activity 
get the auction activity 
-------------------------------------------------------------------------------
'''
group_df_bid1=df_bid_1.groupby('ID')
col_bid_info=['ID','bidder_act','len_act','bidder_pos','bidder_state','bidder_price']

df_bid_info_t=pd.DataFrame(columns=col_bid_info)

# 38265652208
for id_ele in group_df_bid1.groups.keys():

#ID_index='40133084923'
    temp_df=group_df_bid1.get_group(id_ele)
    temp_df=temp_df.sort_index(ascending=False)
    bidder_act= temp_df['bidder_id'].tolist()
    # get the player bidding activity  
    bidder_pos=list(list_duplicates(bidder_act))
    bidder_price=temp_df['price'].tolist()
    bidder_price=[float(x.replace(',','')) for x in bidder_price]
    # replace the bidder name
    dict_name={}
    bidder_name_count=0
    for ele in bidder_pos:
        dict_name[ele[0]]=bidder_name_count
        bidder_name_count += 1
    
    bidder_act1=[dict_name.get(n, n) for n in bidder_act]
    length_act=len(bidder_act1)
    # get the last state for each bidder: 
    bidder_state=[]
    bidder_pos1=[]
    for ele in bidder_pos:
        bidder_pos1.append(tuple([dict_name[ele[0]],ele[1]]))
        bidder_state.append(ele[1][-1])
    
    temp_row=pd.Series([id_ele, bidder_act1, length_act, bidder_pos1, bidder_state,bidder_price], index=col_bid_info )
# I think I can make the bid_info into a big dataframe 
    df_bid_info_t=df_bid_info_t.append(temp_row,ignore_index=True)


# get the auction information 

info_name=['evaluation_price','reserve_price','bid_ladder','ID','finish_time','incharge_court','lgt','lat','win_bid','num_bidder','priority_people','status']
df_auction_1_c=df_auction_1[info_name]


'''
-------------------------------------------------------------------------------
merge the data
-------------------------------------------------------------------------------
'''
df_bid_info_t.ID=df_bid_info_t.ID.astype(str)
#df_auction_1_c=df_auction_1_c.mask(df_auction_1_c.eq('None')).dropna(subset=['ID'])
df_auction_1_c.ID=df_auction_1_c.ID.astype(str)
merg_df_1=df_bid_info_t.merge(df_auction_1_c,left_on='ID',right_on='ID',how='inner')

# it seems merge_df has some unsupported type for sqlite 
#con_merge_clean = sqlite3.connect("G:/auction/clean/est.sqlite")
#merg_df_1.to_sql('test_raw',con_merge_clean,if_exists="replace")

# use hdf to save the data
merg_df_1.to_hdf('G:/auction/clean/est.h5',key='test_raw',mode='w')

test_df_merge=pd.read_hdf('G:/auction/clean/est.h5',key='test_raw')