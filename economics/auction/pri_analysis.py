# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 20:45:58 2018

@author: xiaofeima
This script is aimed at analyzing the priority people behavior.
The objetive here is to find some evidence for asymmetric information

"""


# package 
import sqlite3
import pandas as pd
import numpy as np
import time, re,copy
import matplotlib.pyplot as plt


#load the data
store_path="E:/auction/"

graph_path = "E:/Dropbox/academic/ideas/IO field/justice auction/draft/pic/"

con = sqlite3.connect(store_path+"auction_info_house.sqlite")

PATH_output="E:\\Dropbox\\academic\\ideas\\IO field\\justice auction\\code2\\analysis\\"

df_1_s = pd.read_csv(PATH_output+"sample1_df.csv", sep='\t', encoding='utf-8')
df_2_s = pd.read_csv(PATH_output+"sample2_df.csv", sep='\t', encoding='utf-8')
df_1_s['p_ratio']=df_1_s['win_bid']/df_1_s['reserve_price']
df_2_s['p_ratio']=df_2_s['win_bid']/df_2_s['reserve_price']



# get the distribution between priority people and non-priority people
pri_group1 = df_1_s.groupby("priority_people")
pri_group2 = df_2_s.groupby("priority_people")

# graph for number of bidder
plt.subplot(121) 
graph_1=pri_group1.num_bidder.plot.density(ind=[1,2,3,4,5,6,7,8,9,10],legend=True)
plt.margins(0.02)
plt.xlabel("number of bidder")
plt.title("First Time Auction")
plt.grid(True)
# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_numbidder_1.png")


plt.subplot(122) 
graph_2=pri_group2.num_bidder.plot.density(ind=[1,2,3,4,5,6,7,8,9,10],legend=True)
plt.xlabel("number of bidder")
plt.title("Second  Time Auction")
plt.margins(0.02)
plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()


# save the graph independent
#fig=graph_2[0].get_figure()
#fig.savefig(graph_path+"priori_numbidder_2.png")



# graph for reserve proxy
plt.subplot(121) 
graph_1=pri_group1.p_ratio.plot.density(xlim=[0,2],legend=True)
plt.margins(0.02)
plt.xlabel("winning price / reserve price")
plt.title("First Time Auction")
plt.grid(True)
# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_rese_proxy_1.png")

plt.subplot(122)
graph_2=pri_group2.p_ratio.plot.density(xlim=[0,2],legend=True)
plt.xlabel("winning price / reserve price")
plt.title("Second  Time Auction")
plt.margins(0.02)
plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()
# save the graph independent
#fig=graph_2[0].get_figure()
#fig.savefig(graph_path+"priori_rese_proxy_2.png")


# graph for bidding spread
graph_1=pri_group1.dist_high.plot.density(xlim=[-10,200],legend=True)
fig=graph_1[0].get_figure()
fig.savefig(graph_path+"priori_bid_spread.png")


# bid_freq 
graph_1=pri_group1.bid_freq.plot.density(xlim=[-10,500],legend=True)
fig=graph_1[0].get_figure()
fig.savefig(graph_path+"priori_bid_freq.png")












# bidding activity test
# transh

con = sqlite3.connect(store_path+"auction_info_house.sqlite")
con_bid_info = sqlite3.connect(store_path+"bid_house_info.sqlite")

# load the data
cursor = con.cursor()
tab_name=cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in tab_name:
    tab_name_list.append(name[0])
    

df_1 = pd.read_sql_query("SELECT * from shenzhen_1", con)

df_1_bid = pd.read_sql_query("SELECT * from shenzhen_1", con_bid_info)


# get priority people ID 
df_1_group=df_1.groupby("priority_people")
pri_id=df_1_group.get_group(1).ID.tolist()

df_1_bid_group=df_1_bid.groupby("ID")

bid_df_stat=pd.DataFrame(columns=["ID","dis_var",'bid_freq'])

temp_df=df_1_bid_group.dist_high.std()
temp_df=pd.DataFrame(temp_df)
temp_df['bid_freq'] =df_1_bid_group.position.max()+1
temp_df=temp_df.reset_index()    
