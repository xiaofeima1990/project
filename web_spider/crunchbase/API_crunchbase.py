# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 11:52:34 2018

@author: xiaofeima

API data collecting for crunchbase
user_key=6c9ef18c935a0d984d463dd6bb872638
This saves scrapping procedure for different categories 

# organization info
# headqurater location
# funding round
# acquisition
# industry category

"""
import requests
import pandas as pd
import copy, time 
import json
import util

## 
STRUCT_expand={
"organization":"/organizations",
"people":"/people",
"categories":"/categories",
"location":"/locations",
"funding-round":"/funding-rounds",
"acquisition":"/acquisitions",
"ipo":"properties",
"fund":"/funds"
}

API_Prefix="https://api.crunchbase.com/v3.1"
User_key="2bddce7174abaf499d47ed2a4baf4581"

class API_source:
    def __init__(self,api_section,user_key=User_key):
        self.api_url = API_Prefix+STRUCT_expand[api_section]
        self.user_key = user_key
        self.api_section = api_section

    def api_data_collect(self,query_para,flag_status):
        '''
        get info from crunchbase
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            page_info
                indicating the page information we need in the next run
            df_temp
                dataframe we collect 
        '''
        # get the raw data 
        # start_url = self.api_prefix + API_ENDPOINT['ipo']
        query_para["user_key"] = User_key
        key_word = STRUCT_expand[self.api_section]
        flag,raw_json = util.get_raw_data(self.api_url,query_para)
        if flag == 0:
            return 0,"",""
        else:
            page_info, data_info = util.meta_info(raw_json,flag_status)

            df_temp = pd.Dataframe(data_info)
            df_temp=pd.concat([df_temp.drop([key_word],axis=1),df_temp[key_word].apply(pd.Series)],axis=1)

        if page_info["next_page_url"]:
            self.api_url = page_info["next_page_url"]

            return 1,page_info,df_temp

