# -*- coding: utf-8 -*-
"""
Created on Wed May  9 00:06:07 2018

@author: xiaofeima
get detailed information from justice auction

"""

import os

current_path=os.path.dirname(os.path.abspath('__file__'))

import sys

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
import time, re
from datetime import date, timedelta,datetime
from selenium import webdriver

from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
import selenium.common.exceptions as S_exceptions
import pandas as pd
import sqlite3



AUCTION_INFO1={
    'win_bid':'#sf-price > div > p.i-info-wrap.i-left > span',
    'num_bidder':'#page > div:nth-child(7) > div > div > div:nth-child(2) > div.pm-remind > span.pm-apply.i-b > em',
    'reserve_price':'#J_HoverShow > tr:nth-child(1) > td:nth-child(1) > span.pay-price > span',
    'evaluation_price':'#J_HoverShow > tr:nth-child(3) > td:nth-child(1) > span.pay-price > span',
    'bid_ladder':'#J_HoverShow > tr:nth-child(1) > td:nth-child(2) > span.pay-price > span',
    
    'delay_count':'#J_Delay > em',
    

}
finish_time='#page > div:nth-child(7) > div > div > div.pm-main-l.auction-interaction > ul > li:nth-child(2) > span.countdown.J_TimeLeft'
incharge_court='c-department'
#incharge_court='#page > div:nth-child(7) > div > div > div.pm-main-l.auction-interaction > div.pai-info > p:nth-child(2) > a'

announce='#NoticeDetail'
location='J_Coordinate'
result='div.confirm-content'
property_name='#J_Confirmation > div.J_ConfirmContent > div > div > div > p.c-name'
AUCTION_INFO2={ 
    
    'property_name':'#J_desc > table > tbody > tr:nth-child(1) > td:nth-child(2) > p > span:nth-child(1) > span',
    'source':'#J_desc > table > tbody > tr:nth-child(2) > td:nth-child(2) > p > span > span',
#    'land_usage':'#J_desc > table > tbody > tr:nth-child(5) > td:nth-child(3) > p',
    'win_bidder':'#J_Confirmation > div.J_ConfirmContent > div > div > div > p.c-content'
        }

priority_info="td.prior-td"
col_name=['ID','win_bidder_id']+list(AUCTION_INFO1.keys())+['incharge_court','lat','lgt','property_name','win_bidder','land_usage','announce',]
col_bid=['status','bidder_id','price','date','time']
location_nav1='#J_DetailTabMenu > li.first > a'
location_nav2='#J_DetailTabMenu > li:nth-child(3) > a'
location_nav3='#J_DetailTabMenu > li:nth-child(4) > a'
location_nav4='#J_DetailTabMenu > li:nth-child(5) > a'

page_load_flag="#sf-foot-2014 > div > div > div.bottom-list-row.row2 > h3"

bidding_table='#J_RecordList > tbody'
bidding_next='#J_PageContent > li:nth-child(2) > a'

# it seems I can only run from the ipython 
def open_page(driver,url):
    # only firefox is OK !!! 
    # driver.implicitly_wait(5)
#    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[3]/div[4]/a[7]")))
    try:
        driver.set_page_load_timeout(5)
        driver.get(url)
    except TimeoutException as ex:
        check=driver.find_element_by_css_selector(page_load_flag)
        if not check :
            print("problem with the page, restart it")
            driver.quit()
        driver.execute_script("window.stop();")
    
    return driver



def get_info(driver,link_url):
    '''
    df_info1 : auction info ingeneral
    df_info2 : bidding table
    '''
    
    df_info1=pd.DataFrame(columns=col_name)
    driver=open_page(driver,link_url)
    # df1 for basic infomation
    
    # column 1
    
    for name,ele in AUCTION_INFO1.items():
        candi_info=driver.find_element_by_css_selector(ele).text
        df_info1.loc[0,name]=int(candi_info.replace(",",""))
    df_info1.loc[0,'finish_time']=driver.find_element_by_css_selector(finish_time).text
    
    tmp_pri=driver.find_element_by_css_selector(priority_info).text.split(":")
    if "无" in tmp_pri[1]: 
        df_info1.loc[0,'priority_people']=0
    else:
        df_info1.loc[0,'priority_people']=1
    
    # column 2
    
    driver.find_element_by_css_selector(location_nav1).click()
    time.sleep(1)
    notice_detail=driver.find_element_by_css_selector(announce).text
    df_info1.loc[0,'announce']=notice_detail
    
    # detail info
    driver.find_element_by_css_selector(location_nav2).click()
    time.sleep(1)
    df_info1.loc[0,['lat','lgt']]=driver.find_element_by_id(location).get_attribute("value").split(",")
    
    driver.find_element_by_css_selector(location_nav4).click()
    time.sleep(1)
    df_info1.loc[0,'incharge_court']=driver.find_element_by_class_name(incharge_court).text.split("：")[1]
    res=driver.find_element_by_css_selector(result).text
    df_info1.loc[0,'win_bidder']=re.findall(r'用户姓名(?P<name>.*)通过',res)[0]
    df_info1.loc[0,'win_bidder_id']=re.findall(r'通过竞买号(?P<name>.*)于2',res)[0]
    temp=driver.find_element_by_css_selector(property_name).text
    df_info1.loc[0,'property_name']=re.findall(r'标的物名称：(?P<name>.*)',temp)[0]
    # info2 bidder activity
    driver.find_element_by_css_selector(location_nav3).click()
    
    flag=1
    df_info2=pd.DataFrame(columns=col_bid)
    while flag==1:
        df_temp=pd.DataFrame(columns=col_bid)
        table_content=driver.find_element_by_css_selector(bidding_table).text
        
        table_content=table_content.split()
        for j in range(0,int(len(table_content)/5)):
            df_temp.loc[j]=table_content[j*5:j*5+5]
            
            
        df_info2=df_info2.append(df_temp,ignore_index=True)
        
        try:
            driver.find_element_by_css_selector(bidding_next).click()
            driver.implicitly_wait(3)
            time.sleep(1)
        except:
            flag=0
            
        
    ## get id infomation
    id_info=re.findall(r'\d+',link_url)[0]
    
    return (df_info1,df_info2,id_info)
    
firefoxdriver_path="E:\\github\\Project\\web_spider\\land auction taobao\\"

driver=webdriver.Firefox(firefoxdriver_path)

city="your city "
base_url="https://sf.taobao.com/sf_item/548131372870.htm"

#driver=open_page(driver,base_url)


(df_info1,df_info2,id_info)=get_info(driver,base_url)

## how to save for the data especially for the auction data 
# http://www.datacarpentry.org/python-ecology-lesson/08-working-with-sql/

store_path="E:/auction/"
con = sqlite3.connect(store_path+"auction_info.sqlite")
con2 = sqlite3.connect(store_path+"auction_bidding.sqlite")
df_info2.to_sql(id_info, con2, if_exists="replace")

df_info1.to_sql(city, con, if_exists="append")

# Be sure to close the connection
con.close()
con2.close()