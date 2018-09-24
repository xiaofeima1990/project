# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 08:55:34 2018

@author: xiaofeima
auction data analysis 

data features 
1. high concentration on reserved price
2. large variance in stage 1 auction
3. many unsuccessful sells

deep analysis 
* see the bidder number and winning price distribution 
* the situation that second time auction exceed first time auction
* the situation that first, second time auction exceed evaluation price 


"""

import sqlite3
import pandas as pd
import time, re,copy


link_path="E:/auction/link/"

store_path="E:/auction/"



## connect to the sqlite
#con = sqlite3.connect(store_path+"auction_info.sqlite")
con = sqlite3.connect(store_path+"auction_info.sqlite")

con1 = sqlite3.connect(store_path+"auction_bidding_1_land.sqlite")
con2 = sqlite3.connect(store_path+"auction_bidding_2_land.sqlite")



# Load the data into a DataFrame
df_1 = pd.read_sql_query("SELECT * from xuzhou_1", con)
df_2 = pd.read_sql_query("SELECT * from xuzhou_2", con)

# Be sure to close the connection
con.close()
con2.close()


'''
test for the high concentration first
filter those wrong data : eg. reserve > eval not those reserv/ eval < 80% in first stage 

define index : 
    p_res_eva = reserve / eva
    resev_proxy = (win_bid - reserve)/ reserv

'''
necessary_col=['index','num_bidder','n_register','priority_people','reserve_price','win_bid','evaluation_price']

## check the reserve price situation
df_1['p_res_eva']=df_1['reserve_price']/df_1['evaluation_price']
df_2['p_res_eva']=df_2['reserve_price']/df_1['evaluation_price']


df_1['resev_proxy'] = (df_1['win_bid']-df_1['reserve_price'])/df_1['reserve_price']
df_2['resev_proxy'] = (df_2['win_bid']-df_2['reserve_price'])/df_2['reserve_price']

df_1.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)
df_2.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)

df_1_done=df_1.loc[df_1['status']=="done",['p_res_eva','resev_proxy']+necessary_col]
df_2_done=df_2.loc[df_2['status']=="done",['p_res_eva','resev_proxy']+necessary_col]

df_1_done.plot.scatter(x="num_bidder",y='resev_proxy',c=df_1_done['index'],colormap='viridis')



# see the concentration around reserve price 

df_1_done_1=df_1_done.loc[df_1_done['p_res_eva']<=1,]
df_1_pic1=df_1_done_1.loc[df_1_done_1['resev_proxy']<0.01,]

df_1_pic1['resev_proxy'].hist()
df_1_pic1.plot.scatter(x="num_bidder",y='resev_proxy',s=df_1_pic1['index']*10)


# see the concentration situation under 0.8<reserver / eva <1 
df_1_c=df_1.loc[df_1['p_res_eva']<1,]
df_1_c=df_1_c.loc[df_1_c['p_res_eva']>=0.8,]
df_1_c_done=df_1_c.loc[df_1_c['status']=="done",]

df_1_c_done.plot.scatter(x="num_bidder",y='resev_proxy',c=df_1_c_done['index'],colormap='Blues')
df_1_c_done['resev_proxy'].hist()


        
## winning bid exceed eva distirbution 
df_1_done['p_ratio1']=df_1_done['win_bid']/df_1_done['evaluation_price']
## check the ratio of 

#tail1=df_1_done['p_ratio1'].quantile(.99)  
 
df_1_done_h = df_1_done.loc[df_1_done['p_ratio1']>1,]


df_1_done_h['p_ratio1'].hist(color="#1f77b4",bins=25)


## selected winning bid exceed eva 
df_1_c_done['p_ratio1']=df_1_c_done['win_bid']/df_1_c_done['evaluation_price']
#tail1=df_1_c_done['p_ratio1'].quantile(.99)      
df_1_c_done_h = df_1_c_done.loc[df_1_c_done['p_ratio1']>1,]    

df_1_c_done_h['p_ratio1'].hist(color="#1f77b4",bins=25)

      
# test priorty people effect no statsitical difference 
group_df_1_c=df_1_c.groupby(["priority_people"])

group_df_1_c.median()


# group by time and number of bidder 
group_df_1_c=df_1_c.groupby(["num_bidder"])


             
             
'''
check how many winning bids in stage 2 auction exceed the stage 1 reserve price / eva price
first thing is to build the connection between stage 1 and stage 2 
second do the test

'''             






             