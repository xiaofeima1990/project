# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 23:14:48 2018

@author: xiaofeima
for link and abstract info spider
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
page_load_flag="#sf-foot-2014 > div > div > div.bottom-list-row.row2 > h3"
page_sum_class_name="page-total"
#file_path="E:\\"
# need chromedriver no exe!

firefoxdriver_path="E:\\github\\Project\\web_spider\\land auction taobao\\"




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


col_name_abs=['ID','url','num_bids','status','win_bid','eval_price','n_watch','n_resigter','title','date','time','year']

def get_abs_info(driver,start_page,file_path,file_name,write_flag,Year):
    # get whole link page number 
    summary_link=int(driver.find_element_by_class_name(page_sum_class_name).text)
    df_link=pd.DataFrame(columns=col_name_abs)
    if write_flag==1:
        df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',index=False)
        
    page_count=start_page
    date_flag=0
    
    while page_count<=summary_link:


        try: # to avoid StaleElementReferenceException:
            time.sleep(2)
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
            

                df_temp.loc[i]=[id_info,href,bid_tips,status,win_bid,eval_price,n_watch,n_resigter,title,date1,time1,Year]
            
            df_link=df_link.append(df_temp,ignore_index=True)
            
            
            if (page_count)% 5 ==0:
                # output 
                
                df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
                df_link=pd.DataFrame(columns=col_name_abs)
            if (page_count==summary_link) and summary_link % 5 !=0:
                df_link.to_csv(file_path+file_name+'.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
            
            # open next page
            if page_count==summary_link:
                page_count=page_count+1;
            else:
                try:
        #            driver.find_element_by_css_selector(next_page_css).click()
                    check=driver.find_element_by_css_selector(next_page_css)
                    check.click()
                    time.sleep(2)
#                    driver.execute_script("window.stop();")
                except :
                    check=driver.find_element_by_class_name(page_sum_class_name)
                    if not check :
                        print("problem with the page, restart it")
                        return
            driver.execute_script("window.stop();")        
            page_count=page_count+1;
        except StaleElementReferenceException as e:
            
            print(e)
            print(df_link) 
            print(id_total)
            print(df_link)
            continue
            # refresh current pages 
            
            
                





if __name__ == '__main__':

#base_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504.filter.49.lgLDTu&category=50025970&sorder=2&auction_start_seg=-1"
    start_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504.miniNav.14.m3SaXN&category=50025969&city=%D0%EC%D6%DD&sorder=2&st_param=2&auction_start_seg=0&auction_start_from=2014-01-01&auction_start_to=2014-12-31"
    file_path="E:\\Dropbox\\"
    driver=webdriver.Firefox(firefoxdriver_path)
#    driver=open_page(driver,start_url)
#    con = sqlite3.connect("E:\\justice_auction.sqlite")
    location_code=['520321','520327','520328','520329','520381','520382']
    time_period=['2014-01-01','2014-12-30','2017-07-01','2018-04-18']
#    location_code=['520321','520322','520323','520324','520325','520326','520327','520328','520329','520381','520382']
#    for ele in location_code:
#        for j in range(0,2):
#            base_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504&location_code="+ele+"&category=50025969&city=&province=&sorder=2&auction_start_seg=0"
#            time_url="&auction_start_from="+time_period[2*j+0]+"&auction_start_to="+time_period[2*j+1]
#            start_url=base_url+time_url
#            driver=open_page(driver,start_url)
#        
#            start_page=1
#            write_flag=1 # 1 means new file # 0 means add on 
#            file_name=ele+"-"+str(j)+"-sf" 
#            get_abs_info(driver,start_page,file_path,file_name,write_flag)
    
    # this even requires gbk decoding encoding!!! to convert str to url
    city_name=["徐州","苏州","无锡","淮安","常州","连云港","南京","宿迁","盐城","泰州","扬州","镇江","南通"]
    year_list=['2014','2015','2016','2017']
    for ele in city_name:
        elee=ele.encode("gbk")
        elee=urllib.parse.quote(elee)
        base_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504.miniNav.14.m3SaXN&category=50025969&city="+elee+"&sorder=2&st_param=2&auction_start_seg=0"

        for y in year_list:
            start_time =datetime.strptime(y+'-01-01', '%Y-%m-%d')
            end_time   =start_time+relativedelta(years=1)-timedelta(days=1)
            time_url="&auction_start_from="+start_time.strftime("%Y-%m-%d")+"&auction_start_to="+end_time.strftime("%Y-%m-%d")
            start_url=base_url+time_url
            driver=open_page(driver,start_url)
        
            start_page=1
            
            write_flag=1
            file_name=ele+"-sf" 
            get_abs_info(driver,start_page,file_path,file_name,write_flag,y)
