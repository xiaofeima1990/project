#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 08:31:22 2018

@author: xiaofeima
"""


import os

current_path=os.path.dirname(os.path.abspath('__file__'))

import sys

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
from datetime import date, timedelta,datetime  
from dateutil.relativedelta import relativedelta  
import time, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException,StaleElementReferenceException
import pandas as pd
import sqlite3
import urllib
'''
key parameters 
'''

list_link_path="/html/body/div[3]/div[3]/div[3]/ul/li"
next_page_css="body > div.sf-wrap > div.pagination.J_Pagination > a.next"
page_load_flag="body > div.sf-wrap > div.pagination.J_Pagination > span.page-skip > em"
page_sum_class_name="page-total"
select_page_css = "body > div.sf-wrap > div.pagination.J_Pagination > span.page-skip > label > input"
select_page_sure = "body > div.sf-wrap > div.pagination.J_Pagination > span.page-skip > button"
#file_path="E:\\"
# need chromedriver no exe!

#firefoxdriver_path="E:\\github\\Project\\web_spider\\land auction taobao\\"




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


col_name_abs=['ID','url','num_bids','status','win_bid','eval_price','n_watch','n_resigter','title','date','time','year','flag_time']

def get_abs_info(driver,start_page,file_path,file_name,Year,flag_time):
    # get whole link page number 
    summary_link=int(driver.find_element_by_class_name(page_sum_class_name).text)
    df_link=pd.DataFrame(columns=col_name_abs)
#    if write_flag==1:
#        df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',mode='a',index=False)
#        
    page_count=start_page
    date_flag=0
    if start_page >1 :
        flag_select = 1
    else:
        flag_select = 0
    
    while page_count<=summary_link:



        try: # to avoid StaleElementReferenceException:
            if flag_select == 1:
#                driver.execute_script('window.localStorage.clear();')
                driver=next_page(driver,page_count,flag_select)
                page_count=page_count
                flag_select = 0
            else:
                time.sleep(1)
                content_list=driver.find_elements_by_xpath(list_link_path)
    
    
                n=len(content_list)
                df_temp=pd.DataFrame(columns=col_name_abs)
                for i in range(0,n):
                    status=content_list[i].get_attribute('class').split("-")[-1]
                    id_info=content_list[i].get_attribute('id').split("-")[-1]
                    id_total=content_list[i].get_attribute('id')
                    if 'done' in status:
                        bid_tips=content_list[i].find_elements_by_class_name('pai-xmpp-bid-count')[1].text
                    else:
                        bid_tips=0;
                        
            #            id_link=content_list[i].get_attribute('id')
            
                    try:
                        eval_price=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[4]/span[2]/em[2]").text
                        eval_price=re.findall(r'\d*',eval_price)[0]
                    except :
                        date_flag=1
                        eval_price="NaN"
            
            
                    href=content_list[i].find_element_by_tag_name('a').get_attribute('href')
                    title=content_list[i].find_element_by_css_selector("p.title").text
                    win_bid=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[3]/span[2]/em[2]").text
                    win_bid=re.findall(r'\d*',win_bid)[0]
                    n_watch=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[3]/p/em").text
                    n_resigter=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[3]/p[2]/em").text
                    
                    if date_flag==1:
                        date_all=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[6]/span[2]").text
                        (date1,time1)=date_all.split(" ")
                        date_flag=0
                    else:
                        date_all=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[7]/span[2]").text
                        (date1,time1)=date_all.split(" ")
                
    
                    df_temp.loc[i]=[id_info,href,bid_tips,status,win_bid,eval_price,n_watch,n_resigter,title,date1,time1,Year,flag_time]
                
                df_link=df_link.append(df_temp,ignore_index=True)
                
                
                if (page_count)% 10 ==0:
                    # output 
                    
                    df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
                    df_link=pd.DataFrame(columns=col_name_abs)
                if (page_count==summary_link) and summary_link % 5 !=0:
                    df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
                
                # open next page
                if page_count==summary_link:
                    page_count=page_count+1;
                else:
                    
                    driver=next_page(driver,page_count,flag_select)
                    page_count=page_count+1
                    driver.execute_script('window.localStorage.clear();')

            
        except StaleElementReferenceException as e:
            print("---------")
            print(page_count)
            print(e)
            continue
            
            # refresh current pages 
            
            
                
def next_page(driver,page_count,flag):
    try:
        if flag == 0:
        
            check=driver.find_element_by_css_selector(next_page_css)
            check.click()
        
        else:
            check=driver.find_element_by_css_selector(select_page_css)
            check.send_keys(str(page_count))
            check=driver.find_element_by_css_selector(select_page_sure)
            check.click()
        
        
        
        driver.implicitly_wait(3)
        driver.execute_script("window.stop();")
        
        
        
        
    except TimeoutException as e:
        time.sleep(2)
        driver.execute_script("window.stop();")
        print("current page = "+ str(page_count) +"\t||\t"+"next    page = "+ driver.find_element_by_class_name("current").text)
        
    
    return driver
                    

if __name__ == '__main__':

    file_path="E:\\Dropbox\\"
    
#    con = sqlite3.connect("E:\\justice_auction.sqlite")
    
#     this even requires gbk decoding encoding!!! to convert str to url
#    city_name=["广州","郑州","厦门","福州","常州","南京","盐城","泰州","扬州","镇江","南通"]
    # '温州','绍兴', "湖州", 
    city_name=["佛山","东莞","中山","珠海","江门","肇庆","惠州","汕头","潮州","揭阳","汕尾","湛江","茂名","阳江","韶关","清远","云浮","梅州","河源"]
    
#    ele=input("input city name: ")
    flag_auction_time=input("input auction time choice: 1- first time, 2- second time, 3- 1+2, : ")
    error_page=input('start page')
    error_year=input('error occur year ')
    error_page=int(error_page)
    
    driver=webdriver.Firefox()
#    driver = webdriver.PhantomJS()
    for ele in city_name:
        print("-----------------------------------")
        print("city "+ele+ " begins")
        print("-----------------------------------")
        error_flag = 0
        year_list=['2014','2015','2016','2017']
        #    for ele in city_name:
        elee=ele.encode("gbk")
        elee=urllib.parse.quote(elee)
        # 按竞价次数，第一次第二次拍卖，
        if flag_auction_time=="1":
            auction_time="&circ=%2C1"
        else: 
            if flag_auction_time=="2":
                auction_time="&circ=%2C2"
            
            else:
                auction_time="&circ=1%2C2"
        
        base_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504.miniNav.14.m3SaXN"+auction_time+"&category=50025969&city="+elee+"&sorder=2&st_param=2&auction_start_seg=0"
        
        file_name=ele+"-"+flag_auction_time+"-sf" 
        df_link=pd.DataFrame(columns=col_name_abs)
        df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',mode='a',index=False)
        
        if error_page >1 or error_year >= "2014" :
            error_flag= 1
        
        for y in year_list:
            start_time =datetime.strptime(y+'-01-01', '%Y-%m-%d')
            end_time   =start_time+relativedelta(years=1)-timedelta(days=1)
            time_url="&auction_start_from="+start_time.strftime("%Y-%m-%d")+"&auction_start_to="+end_time.strftime("%Y-%m-%d")
            start_url=base_url+time_url
            driver=open_page(driver,start_url)
            if error_flag == 1:
                if y != error_year:
                    continue
                else:                            
                    start_page=error_page
                    error_page=1
                    error_year="0"
                    error_flag=0
            else:
                    start_page=1
                
        
            print("now the year is : "+y)
            get_abs_info(driver,start_page,file_path,file_name,y,flag_auction_time)
        
        
        
        
        #pause for sometime when we finish one city
        print("-----------------------------------")
        print("city "+ele + " is done ")
        print("-----------------------------------")
        driver.quit()
        time.sleep(10)
        driver=webdriver.Firefox()
    
    driver.quit()
        