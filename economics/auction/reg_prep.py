# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 10:36:44 2018

@author: xiaofeima

data preparation for the reduced form analysis 
priority sample 
DID sample 

"""


import sqlite3
import pandas as pd
import time, re, copy

store_path="E:/auction/"

con = sqlite3.connect(store_path+"auction_info_house.sqlite")


# get the table name 

cursor = con.cursor()
tab_name=cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in tab_name:
    tab_name_list.append(name[0])
    



temp_market=[re.findall(".+_1",x) for x in tab_name_list]
first_market = [item for sublist in temp_market for item in sublist]

temp_market=[re.findall(".+_2",x) for x in tab_name_list]
second_market = [item for sublist in temp_market for item in sublist]



# get all first market data 
flag=0
for city in first_market:
    DF_1_temp = pd.read_sql_query("SELECT * from " +city, con)
    DF_1_temp['city']=city[:-2]
    if flag ==0:
        DF_1 = DF_1_temp.copy()
        flag=1
    else:
        DF_1 = DF_1.append(DF_1_temp,ignore_index=True)

# get all second market data
flag=0
for city in second_market:
    DF_2_temp = pd.read_sql_query("SELECT * from " +city, con)
    DF_2_temp['city']=city[:-2]
    if flag ==0:
        DF_2 = DF_2_temp.copy()
        flag=1
    else:
        DF_2 = DF_2.append(DF_2_temp,ignore_index=True)


'''
clean the data 
'''

DF_1['p_res_eva']=DF_1['reserve_price']/DF_1['evaluation_price']
DF_2['p_res_eva']=DF_2['reserve_price']/DF_2['evaluation_price']

DF_1['resev_proxy'] = (DF_1['win_bid']-DF_1['reserve_price'])/DF_1['reserve_price']
DF_2['resev_proxy'] = (DF_2['win_bid']-DF_2['reserve_price'])/DF_2['reserve_price']

DF_1.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)
DF_2.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)

def yy(x):
    if x is not None:  
        return x[:4]
    else:
        return ""

DF_1['year'] = DF_1['finish_time'].apply(yy)
DF_2['year'] = DF_2['finish_time'].apply(yy)


# select successful auction
DF_1_s=DF_1.loc[DF_1['status']=='done',]
DF_2_s=DF_2.loc[DF_2['status']=='done',]


col_name= ['index', 'ID','n_register','reserve_price','evaluation_price','bid_ladder','p_res_eva', 'resev_proxy','num_bidder','priority_people','status', 'win_bid','city','year','lat','lgt']



DF_1_s=DF_1_s.loc[DF_1_s['p_res_eva']<=1,col_name]
DF_1_s=DF_1_s.loc[DF_1_s['p_res_eva']>=0.7,]
DF_1_s=DF_1_s.loc[DF_1_s['num_bidder']>0,]
DF_1_s=DF_1_s.loc[DF_1_s['resev_proxy']>0.01,]


DF_2_s=DF_2_s.loc[DF_2_s['p_res_eva']<=1,col_name]
DF_2_s=DF_2_s.loc[DF_2_s['p_res_eva']>=0.6,]
DF_2_s=DF_2_s.loc[DF_2_s['num_bidder']>0,]
DF_2_s=DF_2_s.loc[DF_2_s['resev_proxy']>0.01,]



PATH_output="E:\\Dropbox\\academic\\ideas\\IO field\\justice auction\\code4\\analysis\\"
DF_1_s.to_csv(PATH_output+"sample_raw1_df.csv", sep='\t', encoding='utf-8', index=False)
DF_2_s.to_csv(PATH_output+"sample_raw2_df.csv", sep='\t', encoding='utf-8', index=False)



'''
bidding info addin  
add bidding information into the data sample

'''
con_bid_info = sqlite3.connect(store_path+"bid_house_info.sqlite")


cursor = con_bid_info.cursor()
tab_name=cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in tab_name:
    tab_name_list.append(name[0])
    
    
    
temp_market=[re.findall(".+_1",x) for x in tab_name_list]
first_market = [item for sublist in temp_market for item in sublist]

temp_market=[re.findall(".+_2",x) for x in tab_name_list]
second_market = [item for sublist in temp_market for item in sublist]


    
flag=0
for city in first_market:
    DF_1_temp = pd.read_sql_query("SELECT * from " +city, con_bid_info)
    if flag ==0:
        DF_1_bid = DF_1_temp.copy()
        flag=1
    else:
        DF_1_bid = DF_1_bid.append(DF_1_temp,ignore_index=True)


df_1_bid_group=DF_1_bid.groupby("ID")

bid_df_stat=pd.DataFrame(columns=["ID","dis_var",'bid_freq'])

temp_df=df_1_bid_group.dist_high.std()
temp_df=pd.DataFrame(temp_df)
temp_df['bid_freq'] =df_1_bid_group.position.max()+1
temp_df=temp_df.reset_index()    


# merge with DF_1

DF_1_full = DF_1.merge(temp_df,how="right",left_on='ID', right_on ='ID')



DF_1_full['p_res_eva']=DF_1_full['reserve_price']/DF_1_full['evaluation_price']


DF_1_full['resev_proxy'] = (DF_1_full['win_bid']-DF_1_full['reserve_price'])/DF_1_full['reserve_price']


DF_1_full.dropna(subset=['p_res_eva','resev_proxy','dist_high'],inplace=True)




DF_1_full['year'] = DF_1_full['finish_time'].apply(yy)



DF_1_s=DF_1_full.loc[DF_1_full['status']=='done',]



DF_1_s=DF_1_s.loc[DF_1_s['p_res_eva']<=1,col_name+["dist_high","bid_freq"]]
DF_1_s=DF_1_s.loc[DF_1_s['p_res_eva']>=0.7,]
DF_1_s=DF_1_s.loc[DF_1_s['num_bidder']>1,]
DF_1_s=DF_1_s.loc[DF_1_s['resev_proxy']>0.01,]



# merge with DF_2

    
flag=0
for city in second_market:
    DF_2_temp = pd.read_sql_query("SELECT * from " +city, con_bid_info)
    if flag ==0:
        DF_2_bid = DF_2_temp.copy()
        flag=1
    else:
        DF_2_bid = DF_2_bid.append(DF_1_temp,ignore_index=True)


df_2_bid_group=DF_2_bid.groupby("ID")

bid_df_stat=pd.DataFrame(columns=["ID","dis_var",'bid_freq'])

temp_df=df_2_bid_group.dist_high.std()
temp_df=pd.DataFrame(temp_df)
temp_df['bid_freq'] =df_2_bid_group.position.max()+1
temp_df=temp_df.reset_index()    


# merge with DF_1

DF_2_full = DF_2.merge(temp_df,how="right",left_on='ID', right_on ='ID')



DF_2_full['p_res_eva']=DF_2_full['reserve_price']/DF_2_full['evaluation_price']


DF_2_full['resev_proxy'] = (DF_2_full['win_bid']-DF_2_full['reserve_price'])/DF_2_full['reserve_price']


DF_2_full.dropna(subset=['p_res_eva','resev_proxy','dist_high'],inplace=True)

DF_2_full['year'] = DF_2_full['finish_time'].apply(yy)

DF_2_s=DF_2_full.loc[DF_2_full['status']=='done',]

DF_2_s=DF_2_s.loc[DF_2_s['p_res_eva']<=1,col_name+["dist_high","bid_freq"]]
DF_2_s=DF_2_s.loc[DF_2_s['p_res_eva']>=0.7,]
DF_2_s=DF_2_s.loc[DF_2_s['num_bidder']>1,]
DF_2_s=DF_2_s.loc[DF_2_s['resev_proxy']>0.01,]