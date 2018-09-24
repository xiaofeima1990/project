# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 13:27:44 2018

@author: gum27
checking the maximu activity intervals 
"""
import pandas as pd
import re
import copy
import sqlite3
import numpy as np



# school
store_path='X:\\My Documents\\guoxuanma\\my paper\\justice auction\\auction\\'


## connect to the sqlite
con = sqlite3.connect(store_path+"auction_bidding_house.sqlite")

### list table names 
res = con.execute("SELECT name FROM sqlite_master WHERE type='table';")
for name in res:
    print(name[0])




# Load the data into a DataFrame
df_1 = pd.read_sql_query("SELECT * from chengdu_1", con)
df_2 = pd.read_sql_query("SELECT * from chengdu_2", con)

# Be sure to close the connection
con.close()




mask = df_1.ID_info.duplicated(keep=False)

## select more than one bid auction 
mul_df_1= df_1[mask]

## group the mul_df by the ID and check how many bidders 
group_df_1=mul_df_1.groupby(["ID_info"])

bidder_count=group_df_1['bidder_id'].unique()
bidder_count_df=pd.DataFrame(bidder_count.apply(lambda x : len(x)))
bidder_count_df=bidder_count_df.reset_index()

## group by the number of bidders in the auction
group_bid_df=bidder_count_df.groupby('bidder_id')


'''
loop each auction to find maimum intervals
starting from 3,4,5,6,7,... etc biders 


''' 
from collections import defaultdict,OrderedDict

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() 
                            if len(locs)>1)
    

# pick one auction for example 

# the number of bidders you are looking at     
num_bidder= 3
temp_ID_auction=group_bid_df.get_group(num_bidder)

for auction_ID in temp_ID_auction['ID_info']:
    
    # get the auction data  extract the bidder sequence 
    bidders_list= group_df_1.get_group(auction_ID)['bidder_id'].tolist()
    
    # always keep the list in order
    # the first one is the winning bidder
    # the second one is the second highest
    x=list(list_duplicates(bidders_list))
    
    diff_dict=OrderedDict()
    max_diff=[]
    for xx in x:
        temp_1=np.diff(xx[1])
        diff_dict[xx[0]] = temp_1
        # record the max interval for each bidder ignoring those who bid only once
        if temp_1:
            max_diff.append(max(temp_1))


# get record for oder bidders' interval information, and do the loop to check everyone's information 


    
