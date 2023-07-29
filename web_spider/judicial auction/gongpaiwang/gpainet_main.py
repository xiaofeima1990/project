#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 11:58:02 2023

@author: xiaofeima

公拍网 http://www.gpai.net/sf/

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


session = HTMLSession()
base_url = "https://s.gpai.net/sf/search.do?at=376&restate=3"
start_page = 1
raw = session.get(base_url+ "&Page="+ str(start_page))
print(raw.status_code)

raw.html.render(sleep = 3)

next_page = start_page
# -------------------------------------------------------------------------------------------


# find the number of items 
total_items_selector =  "body > div > div:nth-child(7) > div > div.sm-filtbar > div.filtbar-l.fl > span > label"
total_items_num = raw.html.find(total_items_selector,first = True).element.text
print(total_items_num)


## current page
current_page_selector = "body > div > div:nth-child(7) > div > div.page-bar > div " 
current_page_num = raw.html.find(current_page_selector,first = True).find(".on",first = True).element.text 
## total pages 
total_page_selector = "body > div > div:nth-child(7) > div > div.page-bar > div > span.page-infos > label"
total_page = raw.html.find(total_page_selector,first = True).element.text
total_page_num = re.findall('\d+',total_page)[0]




# get the list of items per page 
table_selector = "body > div > div:nth-child(7) > div > div.filt-result-list > ul> li"
table_html = raw.html.find(table_selector)
N_items = len(table_html)


dict_info_selector = {
    "online": "div > span.badge-arrow3",
    "deal":   "div > span.badge-icon.badge-bg137",

    "title":"div > div.item-tit > a",
    "win_price":"div > div.gpai-infos > p:nth-child(2) > b",
    "eval_price":"div > div.gpai-infos > p:nth-child(4) > span:nth-child(2)",
    "end_datetime": " div > div.gpai-infos > p:nth-child(5) > span",
    "weiguan":" div > div.gpai-infos > div > a > div:nth-child(1)",
    "num_bids":"div > div.gpai-infos > div > a > div:nth-child(2)",
    "href":  "div > a", 
}


dict_info_extract = {
    "online":"",
    "deal":"",
    "title":"",
    "auction_stage":"",
    "win_price":"",
    "eval_price":"",
    "end_time":"",
    "end_date":"",
    "weiguan":"",
    "num_bids":"",
    "item_ID":"",
    "index_item":"",

}

stand_cols = ["online",'deal','win_price','eval_price','weiguan','num_bids',"title"]

raw_df = pd.DataFrame()

# extract 
for i in range(0,N_items):
    ele_raw = table_html[i]
    for col_ele in stand_cols:
        dict_info_extract[col_ele] = ele_raw.find(dict_info_selector[col_ele],first = True).text.strip() 

    dict_info_extract['weiguan'] = re.findall("\d+",dict_info_extract['weiguan'])[0]

    item_href=ele_raw.find(dict_info_selector['href'],first=True).attrs['href']
    dict_info_extract['item_ID'] = re.findall("Web_Item_ID=(\d+)",item_href)[0]

    item_title=ele_raw.find(dict_info_selector['title'],first=True).element.text 
    dict_info_extract['auction_stage'] = re.findall("【(\w+)】",item_title)[0]

    item_datetime=ele_raw.find(dict_info_selector['end_datetime'],first=True).element.text
    dict_info_extract['end_date'] = re.findall("\d{4}[/-]\d+[/-]\d+",item_datetime)[0]
    dict_info_extract['end_time'] = re.findall("\d{4}[/-]\d+[/-]\d+ (\d{2}:\d{2}:\d{2})",item_datetime)[0]

    dict_info_extract['index_item'] = i
    dict_info_extract['eval_price'] = dict_info_extract['eval_price'].replace(",","")
    temp_eval = re.findall("\d+\.*\d+",dict_info_extract['eval_price'])[0]
    
    if "万" in dict_info_extract['eval_price']:
        dict_info_extract['eval_price'] = float(temp_eval)*1000
    else:
        dict_info_extract['win_price']  = float(temp_eval)

    temp_df = pd.DataFrame(dict_info_extract,index=[i])

    raw_df = pd.concat([raw_df,temp_df])
# save 

# find the next page info 
next_page_selector = "body > div > div:nth-child(7) > div > div.page-bar > div > a.page-next" 
next_html = raw.html.find(table_selector)
next_page = next_page + 1

if next_page <= int(total_page_num):
    next_page_html = base_url + "&Page="+ str(next_page)
else:
    print("finish")


