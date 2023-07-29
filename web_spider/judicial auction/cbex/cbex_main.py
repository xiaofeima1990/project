#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 11:58:02 2023

@author: xiaofeima

北交互联 https://otc.cbex.com/page/sfpm/list/index.htm?type=jpz

need a lot of javascript 

"""



from requests_html import HTMLSession,AsyncHTMLSession
import pandas as pd
import re
from sys import platform
# path 
if platform == "win32":
    path_prefix = "D:/"
else:
    path_prefix = "/Users/xiaofeima/"
    
path = path_prefix + "Dropbox/work/UIBE/global_production/"
output = path

session = HTMLSession()
base_url = "https://otc.cbex.com/page/sfpm/list/index.html?bdwlx=6"
start_page = 1
raw = session.get(base_url)
print(raw.status_code)

raw.html.render(sleep = 3)


## nav to the zhuzhai and ending status 
# conduct the javascript 

JS_script1 = '''
document.querySelector("[data-value = '6']").click()
'''

JS_script2 = '''
document.querySelector("[data-value = 'yjs']").click()
'''

raw.html.render(retries = 4, script = JS_script1,sleep = 3)
raw.html.render(retries = 4, script = JS_script2,sleep = 3)

auction_stage = {
    '1':"一拍",
    '2':"二拍",
    '3':"变卖",
}

print(raw.html.find("#bdwCount",first= True).element.text)
total_pages = int(raw.html.find("#pagebar > a.pagebtn.pagebtn-name")[-1].attrs['data-next'])
print(total_pages)


#list_li_1BDAEBF4DEED00976F4F7330821C1A78 > div.sfpm_cont > a
dict_info_selector = {

    "title":"div.sfpm_cont > a.title",
    "win_price":"div.sfpm_cont > div > p:nth-child(1) > span ",
    "eval_price":" div.sfpm_cont > div > p:nth-child(2) > span",

    "weiguan":" div.sfpm_info > div:nth-child(1) > span ",

    "num_bids":"div.sfpm_cont > div > div > div > p.sfpm_side_num",
    "num_bidders":"div.sfpm_info > div:nth-child(2) > span",
     
}


DICT_info_extract = {
    "title":"",
    "auction_stage":"",
    "win_price":"",
    "eval_price":"",
    "weiguan":"",
    "num_bids":"",
    "item_ID":"",
    "index_item":"",
}
current_page = 1
count = 0
for stage_i in [1,2,3]:
    JS_script3 = '''
    document.querySelector("#pmjd").querySelector("[data-value = '{}']").click()
    '''.format(stage_i)

    raw.html.render(retries = 4, script = JS_script3,sleep = 3)

    # locate the key positions 
    table_html = raw.html.find('#sfpmList > li ')
    N_items = len(table_html)

    stand_cols = ["title","win_price","eval_price","weiguan","num_bids","num_bidders"]
    raw_df = pd.DataFrame()

    # extract 
    for i in range(0,N_items):
        ele_raw = table_html[i]
        dict_info_extract = DICT_info_extract.copy()
        for col_ele in stand_cols:
            dict_info_extract[col_ele]  = ele_raw.find(dict_info_selector[col_ele],first=True).text

        dict_info_extract['win_price']  = re.findall('[0-9.]*[0-9]+',dict_info_extract['win_price'])[0]
        dict_info_extract['eval_price'] = re.findall('[0-9.]*[0-9]+',dict_info_extract['eval_price'])[0]
        dict_info_extract['weiguan'] = re.findall("[0-9.]*[0-9]+",dict_info_extract['weiguan'])[0]
        dict_info_extract['num_bidders'] = re.findall("[0-9.]*[0-9]+",dict_info_extract['num_bidders'])[0]

        dict_info_extract['item_ID'] = ele_raw.attrs['data-itemno']

        dict_info_extract['auction_stage'] = auction_stage[stage_i]

        dict_info_extract['index_item'] = count


        temp_df = pd.DataFrame(dict_info_extract,index=[count])
        raw_df = pd.concat([raw_df,temp_df])
        count = count +1

    if current_page == 1:
        raw_df.to_csv(path+"cbex_abstract.csv",sep = "|",mode='w',encoding="utf-16",index=False)
        raw_df = pd.DataFrame()

    if (current_page) % 20 == 0:
        print("save temp df at page {}".format(next_page))
        raw_df.to_csv(path+"cbex_abstract.csv",sep = "|",mode='a',encoding="utf-16",index=False,header=False)
        raw_df = pd.DataFrame()

    if (current_page) % 10 == 0:
        time.sleep(10)

    # find the next page info 
    # thsi is for the next page
    JS_script4 = """
    document.getElementsByClassName("pagebtn pagebtn-name")[2].click()
    """
    raw.html.render(retries = 4, script = JS_script4,sleep = 3)
    time.sleep(5)

    # find the ending page 
    current_page_selector = "#pagebar > a.pagebtn.pagebtn-count.pagecount-active"
    current_page = int(raw.html.find(current_page_selector,first = True).element.text)
    
    #pagebar > a.pagebtn.pagebtn-name
    if current_page >= total_pages:
        print("end for stage {}".format(stage_i))
        raw_df.to_csv(path+"cbex_abstract.csv",sep = "||",encoding="utf-16",index=False,header=False)
