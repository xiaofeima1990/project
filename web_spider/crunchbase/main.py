# -*- coding: utf-8 -*-
"""
Created on Thur May 23 11:52:34 2018

@author: xiaofeima

API data collecting for crunchbase
user_key=6c9ef18c935a0d984d463dd6bb872638
This is the main script for data collection

https://data.crunchbase.com/docs/using-the-api
"""
import requests
import pandas as pd
import copy, time
import sqlite3
import json
import util
import API_crunchbase

API_ENDPOINT={
"organization":"/organizations",
"people":"/people",
"categories":"/categories",
"location":"/locations",
"funding-round":"/funding-rounds",
"acquisition":"/acquisitions",
"ipo":"/ipos",
"fund":"/funds"
}
API_WORK_INSTRUCTION={
"1":"organization",
"2":"people",
"3":"categories",
"4":"location",
"5":"funding-round",
"6":"acquisition",
"7":"ipo",
"8":"fund"
}


store_path = "~/dropbox/academic/database/crunchbase"


## specify which data to collect
for ele, key in API_WORK_INSTRUCTION.items():
    print("{}:\t{}".format(ele,key))
section_name=input("input the data section you want to collect")

## get data from api
data_api=API_crunchbase.API_source(API_WORK_INSTRUCTION[section_name])

flag=0
page_num=1
query_para={
	"page":page_num,
    "sort_order":"created_at ASC"
}
## save to the database
stat_flag,page_info,df_summary=data_api.api_data_collect(query_para,flag)
col_name=df_summary.columns
if stat_flag==0:
    print("something wrong, restart the problem")
    exit(1)
flag=1
page_num = page_info["current_page"]
length_page= int(page_info['number_of_pages'])

while page_num <= length_page:
    try:
        stat_flag,page_info,df_temp=data_api.api_organization_collect_summary(query_para,flag)
        if stat_flag==0:
            print("something wrong, restart the problem")
            exit(1)
        df_summary=df_summary.append(df_temp,ignore_index=True)
        page_num = page_info["current_page"]
        if page_num % 10 == 0 or page_num == length_page:
            # connect to database
            con = sqlite3.connect(store_path+"crunchbase.sqlite")
            df_summary.to_sql(str(API_WORK_INSTRUCTION[section_name]), con, if_exists="append")
            con.close()
            df_summary=pd.DataFrame(columns=col_name)
            
    except Exception as e:
        print(e)
        print("the current page is {}".format(page_num))
        print("this is for {}".format(API_WORK_INSTRUCTION[section_name] ))
