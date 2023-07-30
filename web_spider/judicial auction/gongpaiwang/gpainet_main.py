#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 11:58:02 2023

@author: xiaofeima

公拍网 http://www.gpai.net/sf/

"""




from requests_html import HTMLSession,AsyncHTMLSession
import pandas as pd
import numpy as np
import re,time
from sys import platform
# path 
if platform == "win32":
    path_prefix = "D:/"
else:
    path_prefix = "/Users/xiaofeima/"
    
path = path_prefix + "Dropbox/academic/11_work_dataset/justice auction/rawdata2/"

# ------------------------------------------------------------------------------------------
SAVE_link = "https://www.gpai.net/sf/item2.do?Web_Item_ID="
Table_selector = "body > div > div:nth-child(7) > div > div.filt-result-list > ul > li"
DICT_info_selector = {
    "online": "div > span.badge-arrow3",
    "deal":   "div > span.badge-icon",

    "title":"div > div.item-tit > a",
    "win_price":"[class ='price-red' ]",
    "eval_price":"div > div.gpai-infos > p:nth-child(4) > span:nth-child(2)",
    "end_datetime": " div > div.gpai-infos > p:nth-child(5) > span",
    "weiguan":" div > div.gpai-infos > div > a > div:nth-child(1)",
    "num_bids":"div > div.gpai-infos > div > a > div:nth-child(2)",
    "href":  "div > a", 
}


DICT_info_extract = {
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
    "link":"",

}



# -------------------------------------------------------------------------------------------
# function 
# -------------------------------------------------------------------------------------------

def win_price_extraction(ele_raw):
    # win price 成交价/最新价
    temp_win = ele_raw.find(DICT_info_selector['win_price'])[0].text
    temp_win_unit = ele_raw.find(DICT_info_selector["win_price"])[1].text 
    result_price = temp_win.replace(",","")
    # temp_eval = re.findall("[0-9.]*[0-9]+",dict_info_extract['eval_price'])[0]
    if "万" not in temp_win_unit:
        result_price  = float(result_price)
    else:
        result_price  = float(result_price)*10000
            
    return result_price


def eval_price_extraction( ele_raw):
    # eval price 评估价/市场价
    result_price = np.nan
    temp = ele_raw.find("p",containing=r"评估价")
    if len(temp) == 0:
        temp = ele_raw.find("p",containing=r"市场价")
    
    if len(temp) >0:
        temp = temp.replace(",","")
        temp_price  = re.findall("[0-9.]*[0-9]+",temp)[0]
        if "万" not in temp:
            result_price  = float(temp_price)
        else:
            result_price  = float(temp_price)*10000
    else:
        print("not find eval price")
        
    return result_price

def open_page(next_page,session):
    restart_mode = 1
    count_flag = 4
    
    raw = session.get(base_url+ "&Page="+ str(next_page))
    
    while count_flag > 0:   
        if "to complete verification" in raw.html.text:
            restart_mode = 1
            
        table_html = raw.html.find(Table_selector)
        if len(table_html) == 0:
            restart_mode = 1
        else:
            restart_mode = 0
            return raw 
        
        if (restart_mode == 1):
            print("page {} has problem!".format(next_page))
            raw.close()
            time.sleep(5)
            session = HTMLSession()
            raw = session.get(base_url+ "&Page="+ str(next_page))
            raw.html.render(sleep = 5)
        else:
            return raw
    
        count_flag = count_flag - 1
        
    if restart_mode == 1:
        print("bad connection wait and restart later")
        exit()
    else:
        return raw

# -------------------------------------------------------------------------------------------
session = HTMLSession()
base_url = "https://s.gpai.net/sf/search.do?at=376&restate=3"
start_page = 1
raw = session.get(base_url+ "&Page="+ str(start_page))
print(raw.status_code)

raw.html.render(sleep = 3)

next_page = start_page
# -------------------------------------------------------------------------------------------


# find the number of items 

total_items_selector =  "body > div > div:nth-child(7) > div > div.sm-filtbar > div.filtbar-l.fl > span > label "
total_items_num = raw.html.find(total_items_selector,first = True).element.text
print(total_items_num)


## current page
current_page_selector = "body > div > div:nth-child(7) > div > div.page-bar > div " 
current_page_num = raw.html.find(current_page_selector,first = True).find(".on",first = True).element.text 
## total pages 
total_page_selector = "body > div > div:nth-child(7) > div > div.page-bar > div > span.page-infos > label"
total_page = raw.html.find(total_page_selector,first = True).element.text
total_page_num = re.findall('\d+',total_page)[0]
print("total page number is {}".format(total_page_num))



# only contains safe names 
stand_cols = ["online",'deal','win_price','eval_price','weiguan','num_bids',"title"]

raw_df = pd.DataFrame()
count = 0
while next_page <= int(total_page_num):
    # extract 
    print("current page: {} ".format(next_page))
    time.sleep(3)
    raw = open_page(next_page,session)
    # get the list of items per page 
    table_selector = "[class = 'main-col-list clearfix']"
    table_html = raw.html.find(table_selector)[0].find('li')
    N_items = len(table_html)
    # if N_items == 0:
    #     print("problems!!! no info returned! wait for refresh")
    #     raw.close()
    #     session = HTMLSession()
    #     time.sleep(5)
    #     raw = open_page(next_page)
    for i in range(0,N_items):
        dict_info_extract = DICT_info_extract
        ele_raw = table_html[i]
        # a simple way to do so and aovid conflicts 
        raw_info_list = ele_raw.text.split("\n")
        try:
            if len(raw_info_list) == 7:
                # 0 
                raw_info_list[0] = raw_info_list[0].strip()
                (dict_info_extract['online'],dict_info_extract['deal']) = raw_info_list[0].split()
                # 1
                dict_info_extract['title'] = raw_info_list[1]
                dict_info_extract['auction_stage'] = re.findall("【(\w+)】",raw_info_list[1])[0]
                # 2
                temp = raw_info_list[2].replace(",","") 
                temp_price  = re.findall("[0-9.]*[0-9]+",temp)[0]
                dict_info_extract['win_price'] = temp_price
            
                # 3 
                temp = raw_info_list[3].replace(",","") 
                temp_price  = re.findall("[0-9.]*[0-9]+",temp)[0]
                if "万" in temp:
                    dict_info_extract['eval_price']  = float(temp_price)*1000
                else:
                    dict_info_extract['eval_price']  = float(temp_price)
                    
                # 4 
                dict_info_extract['end_date'] = re.findall("\d{4}[/-]\d+[/-]\d+",raw_info_list[4])[0]
                dict_info_extract['end_time'] = re.findall("\d{4}[/-]\d+[/-]\d+ (\d{2}:\d{2}:\d{2})",raw_info_list[4])[0]
                
                # 5
                temp =  re.findall("\d+",raw_info_list[5])
                if len(temp) > 0 : 
                    dict_info_extract['weiguan'] = int(temp[0])
                else:
                    dict_info_extract['weiguan'] = ""
                                            
                # 6
                temp =  re.findall("\d+",raw_info_list[6])
                if len(temp) > 0 :  
                    dict_info_extract['num_bids'] = int(temp[0])
                else:
                    dict_info_extract['num_bids'] = ""
                

        except Exception as ex:
            print(ex)
            print("error place: page: {}, i: {} ".format(next_page,i))
            error_title = ele_raw.find(DICT_info_selector['title'])[0].text
            print("error item title: {} ".format(error_title))
            print("error raw info {}".format(ele_raw.text))
            print(dict_info_extract)
                # 7 
        item_href=ele_raw.find(DICT_info_selector['href'],first=True).attrs['href']
        dict_info_extract['item_ID'] = re.findall("Web_Item_ID=(\d+)",item_href)[0]                
        dict_info_extract['link']    = SAVE_link+dict_info_extract['item_ID']      
              
        dict_info_extract['index_item'] = count
        temp_df = pd.DataFrame(dict_info_extract,index=[count])

        raw_df = pd.concat([raw_df,temp_df])
        count = count + 1
    # save 

    if next_page == 1:
        raw_df.to_csv(path+"gpainet_abstract.csv",sep = "|",mode='w',encoding="utf-16",index=False)
        raw_df = pd.DataFrame()

    if (next_page) % 20 == 0:
        print("save temp df at page {}".format(next_page))
        raw_df.to_csv(path+"gpainet_abstract.csv",sep = "|",mode='a',encoding="utf-16",index=False,header=False)
        raw_df = pd.DataFrame()



    # find the next page info 
    # next_page_selector = "body > div > div:nth-child(7) > div > div.page-bar > div > a.page-next" 
    # next_html = raw.html.find(next_page_selector)
    
    if (next_page) % 10 == 0:
        time.sleep(10)
        session = HTMLSession()
        
    next_page = next_page + 1    
    if next_page > int(total_page_num):
    #     next_page_html = base_url + "&Page="+ str(next_page)
    #     raw = session.get(next_page_html)
    #     # print(raw.status_code, end =" ")    
    #     if raw.status_code != 200:
    #         print("page {} has problem!".format(next_page))
    #         exit()
    #     raw.html.render(sleep = 5)
    #     time.sleep(3)
    # else:
        print("finish")
        raw_df.to_csv(path+"gpainet_abstract.csv",sep = "|",mode='a',encoding="utf-16",index=False,header=False)

