# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 11:52:34 2018

@author: xiaofeima
mengbo Niube

API data collecting for crunchbase
user_key=6c9ef18c935a0d984d463dd6bb872638
"""
import requests
import pandas as pd
import copy, time
import sqlite3
import json



def open_link(url,try_times=10):
    i=0
    while i < try_times:
        r = requests.get(url, params=payload)
        if r.status_code == 200 :
            start_raw=r.json()
            break
        else:
            i +=1
            print("failued to open the url")
            time.sleep(2)
            
    if i>=try_times:
        print(url)
        input("problem, please check the internet and url")
        return ""
    else:    
        return start_raw


store_path= "D:/crunchbase/"

payload = {'user_key': '2bddce7174abaf499d47ed2a4baf4581'}

flag_page= input("start from which page")




r = requests.get('https://api.crunchbase.com/v3.1/ipos?', params=payload)
if r.status_code == 200 :
    start_raw=r.json()

data_raw=start_raw['data']
data_page=data_raw['paging']
data_info=data_raw['items']

num_pag=data_page['number_of_pages']
total_items = data_page["total_items"]
next_page_url=data_page["next_page_url"]
current_page=data_page["current_page"]



    
# get the info
df_1=pd.DataFrame(data_info)
df_full=pd.concat([df_1.drop(['properties'], axis=1), df_1['properties'].apply(pd.Series)], axis=1)
col=df_full.columns

print("current page :  ", flag_page)
current_page=int(flag_page)

if current_page>1: 
    
    next_page_url="https://api.crunchbase.com/v3.1/ipos?page="+flag_page+"&sort_order=created_at%20DESC&items_per_page=100"
    
    df_full=pd.DataFrame(columns=col)
    
while current_page <= num_pag:
    next_page_url=next_page_url+"&"
    start_raw=open_link(next_page_url)
#    r = requests.get(next_page_url, params=payload)
#    if r.status_code == 200 :
#        start_raw=r.json()
    if start_raw == "":
        print("current page is : ", current_page)
        print("restart the program")
        if not df_full.empty:
            con = sqlite3.connect(store_path+"IPO.sqlite")
            df_full.to_sql("IPOs", con, if_exists="append")
            con.close()
        exit()
        
    else:
        
        
        data_raw=start_raw['data']
        data_page=data_raw['paging']
        data_info=data_raw['items']
        
        # get the info
        df_1=pd.DataFrame(data_info)
        df_full_temp=pd.concat([df_1.drop(['properties'], axis=1), df_1['properties'].apply(pd.Series)], axis=1)
        
        df_full=df_full.append(df_full_temp,ignore_index=True)
    
        next_page_url=data_page["next_page_url"]
        current_page=data_page["current_page"]
        print("current page :  ",current_page )
        
        if current_page %20 == 0 or current_page== num_pag :
            # save 
            con = sqlite3.connect(store_path+"IPO.sqlite")
            df_full.to_sql("IPOs", con, if_exists="append")
            con.close()
            
            df_full=pd.DataFrame(columns=col)
            
        
                
          