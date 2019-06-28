# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 11:52:34 2018

@author: Guoxuan

This module saves the method and function that is used 
for data collection and data format conversion
user_key=6c9ef18c935a0d984d463dd6bb872638
"""
import requests
import pandas as pd
import copy, time
import sqlite3
import json

payload = {'user_key': '2bddce7174abaf499d47ed2a4baf4581'}
PAGE_info=["total_items","number_of_pages","current_page","items_per_page","sort_order"]

def get_raw_data(url,para=payload,try_times=3):
    '''
    get the json data from api 
    input arguments:
        url:(required) the api link
        para:(option) the query params that need to specify the url
        try_times:(option) try times if something is wrong
    return variables:
        flag: indicating whether successful or not
        raw: the json metadata
    '''
    i = 0
    while i < try_times:
        try:
            r = requests.get(url, params=para,timeout=2)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)    
            
        if r.status_code == 200 :
            raw = r.json()
            break    
        else:
            time.sleep(5)
            i += 1  
            
    if i >= try_times:
        print(url)
        input("problem, please check the internet and url")
        return 0, ""
    else:    
        return 1, raw


def meta_info(raw_json,flag):
    '''
    extract data info and page info from meta data 
    input arguments:
        raw_json
            the raw json 
        flag
            indicating this is start/restart the process
    return variables:
        page_info
            the page information we need in the next run
        data_info
            the data we need to collect 
    '''
    meta_raw=raw_json['data']
    page_info=meta_raw['paging']
    data_info=meta_raw['items']

    finished = int(page_info["items_per_page"]) * (int(page_info["current_page"])-1) / float(page_info["total_items"])
    if flag == 0:
        print("start/continue the data collection procedure")
        print("total items: {}, finished: {}% ".format(page_info["total_items"],finished ))

    print("processing page: {}/{}, items: {} , finished: {}%".format(page_info["current_page"],page_info["number_of_pages"],page_info["items_per_page"],finished))



    return page_info,data_info


def detail_info(raw_json):
    '''
    extract more detailed info (organization, funding round, fund etc.) from meta data
    input argument: 
        raw_json
            the raw json 
    return variables:
        data_info
            the data we need to collect 
    '''
    meta_raw = raw_json['data']
    type_info = meta_raw['type']
    uuid = meta_raw['uuid']
    property_info = meta_raw['properties']
    relation_ship = meta_raw['relationships']
    print("processing: {} - {}".format(type_info,uuid)) 
    return property_info,relation_ship


def detail_info(raw_json):
    '''
    extract more detailed info (organization, funding round, fund etc.) from meta data
    input argument: 
        raw_json
            the raw json 
    return variables:
        data_info
            the data we need to collect 
    '''
    meta_raw = raw_json['data']
    type_info = meta_raw['type']
    uuid = meta_raw['uuid']
    property_info = meta_raw['properties']
    relation_ship = meta_raw['relationships']
    print("processing: {} - {}".format(type_info,uuid)) 
    return property_info,relation_ship