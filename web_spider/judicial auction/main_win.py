# coding: utf-8
# land auction justice from taobao
# written by Guoxuan Ma
# two steps
# 1 get the link
# 2 get the info

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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
import selenium.common.exceptions as S_exceptions
import pandas as pd
# driver = webdriver.Firefox()


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
    
    return driver


# get link saving land ID and land link and land acution time 
def get_link(driver,start_page,file_path):
    # get whole link page number 
    summary_link=int(driver.find_element_by_class_name(page_sum_class_name).text)
    df_link=pd.DataFrame(columns=['ID','url','auction_counts'])
    df_link.to_csv(file_path+'sf_land_auction.csv', sep='\t', encoding='utf-8',index=False)
    page_count=start_page
    while page_count<summary_link:
    

        
        content_list=driver.find_elements_by_xpath(list_link_path)
        n=len(content_list)
        df_temp=pd.DataFrame(columns=['ID','url','auction_counts','status'])
        for i in range(0,n):
            status=content_list[i].get_attribute('class').split("-")[-1]
            id_info=content_list[i].get_attribute('id').split("-")[-1]
            if 'done' in status:
                bid_tips=content_list[i].find_elements_by_class_name('pai-xmpp-bid-count')[1].text
            else:
                bid_tips=0;
                
#            id_link=content_list[i].get_attribute('id')
            href=content_list[i].find_element_by_tag_name('a').get_attribute('href')
            df_temp.loc[i]=[id_info,href,bid_tips,status]
        
        df_link=df_link.append(df_temp,ignore_index=True)
        
        
        if (page_count-start_page)% 10 ==0:
            # output 
            
            df_link.to_csv(file_path+'sf_land_auction.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
            df_link=pd.DataFrame(columns=['ID','url','auction_counts'])
            
        
        # open next page
        try:
            driver.find_element_by_css_selector(next_page_css).click()
        except TimeoutException as ex:
            check=driver.find_element_by_css_selector(next_page_css)
            if not check :
                print("problem with the page, restart it")
        page_count=page_count+1;

    return id_info


def get_info(driver,link_url_list,store_path,id_info,df_info1,df_info2):
    for i in range(0,len(link_url_list)):
        driver=open_page(driver,link_url_list[i])
        # df1 for basic infomation
        
        # column 1
        
        for name,ele in AUCTION_INFO1.items():
            candi_info=driver.find_element_by_css_selector(ele).text
            df_info1.loc[i,name]=int(candi_info)
        
        df_info1.loc[i,'incharge_court']=driver.find_element_by_css_selector(incharge_court).text
        # column 2
        
        driver.find_element_by_css_selector(location_nav1).click()
        descrition=driver.find_element_by_css_selector(description).text
        df_info1.loc[i,'description']=descrition
        
        # detail info
        driver.find_element_by_css_selector(location_nav2).click()
        df_info1.loc[i,'location']=driver.find_element_by_css_selector(location).text
        
        driver.find_element_by_css_selector(location_nav4).click()
        res=driver.find_element_by_css_selector(result).text
        df_info1.loc[i,'win_bidder']=re.match(r'用户姓名(?P<name>.*)通过',res).group(1)
        df_info1.loc[i,'win_bidder_id']=re.match(r'通过竞买号(?P<name>.*)于',res).group(1)
        temp=driver.find_element_by_css_selector(property_name).text
        df_info1.loc[i,'property_name']=re.match(r'标的物名称：(?P<name>.*)',temp).group(1)
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
                driver.implicitly_wait(1)
            except:
                flag=0
                
            
    
    return (df_info1,df_info2)
    



# base_url="https://sf.taobao.com/"
base_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504.filter.49.lgLDTu&category=50025970&sorder=2&auction_start_seg=-1"

start_url="https://sf.taobao.com/item_list.htm?spm=a213w.7398504.filter.47.tzACTh&location_code=520302&category=50025969&city=&province=&sorder=2&auction_start_seg=-1"

list_link_path="/html/body/div[3]/div[3]/div[3]/ul/li"
next_page_css="body > div.sf-wrap > div.pagination.J_Pagination > a.next"
page_load_flag="#sf-foot-2014 > div > div > div.bottom-list-row.row2 > h3"
page_sum_class_name="page-total"
file_path="E:\\"
# need chromedriver no exe!

firefoxdriver_path="E:\\github\\Project\\web_spider\\land auction taobao\\"

#driver=webdriver.Chrome(chromedriver_path)
driver=webdriver.Firefox(firefoxdriver_path)
driver=open_page(driver,base_url)
driver.get(base_url)


AUCTION_INFO1={
    'win_bid':'#sf-price > div > p.i-info-wrap.i-left > span',
    'num_bidder':'#page > div:nth-child(7) > div > div > div:nth-child(2) > div.pm-remind > span.pm-apply.i-b > em',
    'reserve_price':'#J_HoverShow > tr:nth-child(1) > td:nth-child(1) > span.pay-price > span',
    'evaluation_price':'#J_HoverShow > tr:nth-child(3) > td:nth-child(1) > span.pay-price > span',
    'bid_ladder':'#J_HoverShow > tr:nth-child(1) > td:nth-child(2) > span.pay-price > span',
    'finish_time':'#page > div:nth-child(7) > div > div > div.pm-main-l.auction-interaction > ul > li:nth-child(2) > span.countdown.J_TimeLeft',
    'delay_count':'#J_Delay > em',
    

}
incharge_court='#page > div:nth-child(7) > div > div > div.pm-main-l.auction-interaction > div.pai-info > p:nth-child(2) > a'
description='#J_NoticeDetail > p:nth-child(3)'
location='#J_DetailTabMain > div:nth-child(4) > div:nth-child(6)'
result='#J_Confirmation > div.J_ConfirmContent > div > div > div > p.c-content'
property_name='#J_Confirmation > div.J_ConfirmContent > div > div > div > p.c-name'
AUCTION_INFO2={ 
    
    'property_name':'#J_desc > table > tbody > tr:nth-child(1) > td:nth-child(2) > p > span:nth-child(1) > span',
    'source':'#J_desc > table > tbody > tr:nth-child(2) > td:nth-child(2) > p > span > span',
#    'land_usage':'#J_desc > table > tbody > tr:nth-child(5) > td:nth-child(3) > p',
    'win_bidder':'#J_Confirmation > div.J_ConfirmContent > div > div > div > p.c-content'
        }


col_name=['ID','win_bidder_id']+list(AUCTION_INFO1.keys())+['incharge_court','location','property_name','win_bidder','land_usage','description',]
col_bid=['status','bidder_id','price','date','time']
location_nav1='#J_DetailTabMenu > li.first.current > a'
location_nav2='#J_DetailTabMenu > li:nth-child(3) > a'
location_nav3='#J_DetailTabMenu > li:nth-child(4) > a'
location_nav4='#J_DetailTabMenu > li:nth-child(5) > a'

df_info1=pd.DataFrame(columns=col_name)


bidding_table='#J_RecordList > tbody'
bidding_next='#J_PageContent > li:nth-child(2) > a'
#J_PageContent > li:nth-child(2) > a
info_test_url="https://sf.taobao.com/sf_item/563968765698.htm?spm=a213w.7398504.paiList.23.LQz6Mk"

for name,ele in AUCTION_INFO1.items():
    print(driver.find_element_by_css_selector(ele).text)
    
    
    

col_name_abs=['ID','url','num_bids','status','win_bid','eval_price','n_watch','n_resigter','title','date','time']

def get_abs_info(driver,start_page,file_path):
    # get whole link page number 
    summary_link=int(driver.find_element_by_class_name(page_sum_class_name).text)
    df_link=pd.DataFrame(columns=col_name_abs)
    df_link.to_csv(file_path+'sf_land_auction.csv', sep='\t', encoding='utf-8',index=False)
    page_count=start_page
    date_flag=0
    
    while page_count<=summary_link:


    
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
            href=content_list[i].find_element_by_tag_name('a').get_attribute('href')
            title=content_list[i].find_element_by_css_selector("p.title").text
            win_bid=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[3]/span[2]/em[2]").text
            win_bid=re.findall(r'\d*',win_bid)[0]
            try:
                eval_price=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[4]/span[2]/em[2]").text
                eval_price=re.findall(r'\d*',eval_price)[0]
            except :
                date_flag=1
                eval_price="NaN"
                
            n_watch=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[3]/p/em").text
            n_resigter=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[3]/p[2]/em").text
            
            if date_flag==1:
                date_all=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[6]/span[2]").text
                (date1,time1)=date_all.split(" ")
                date_flag=0
            else:
                date_all=content_list[i].find_element_by_xpath("//li[@id='"+id_total+"']/a/div[2]/p[7]/span[2]").text
                (date1,time1)=date_all.split(" ")
                
            df_temp.loc[i]=[id_info,href,bid_tips,status,win_bid,eval_price,n_watch,n_resigter,title,date1,time1]
        
        df_link=df_link.append(df_temp,ignore_index=True)
        
        
        if (page_count)% 5 ==0:
            # output 
            
            df_link.to_csv(file_path+'sf_land_auction.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
            df_link=pd.DataFrame(columns=col_name_abs)
        if (page_count==summary_link) and summary_link % 5 !=0:
            df_link.to_csv(file_path+'sf_land_auction.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
        
        # open next page
        try:
#            driver.find_element_by_css_selector(next_page_css).click()
            check=driver.find_element_by_css_selector(next_page_css)
            check.click()
            time.sleep(1)
        except :
#            check=driver.find_element_by_css_selector(next_page_css)
            if not check :
                print("problem with the page, restart it")
            
        page_count=page_count+1;
