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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions as S_exceptions
import pandas as pd
import sqlite3



AUCTION_INFO1={
    'win_bid':'span.pm-current-price.J_Price',
    'num_bidder':'div.pm-remind > span.pm-apply.i-b > em',
  #   'reserve_price':'#J_HoverShow > tr:nth-child(1) > td:nth-child(1) > span.pay-price > span',
  #  'evaluation_price':'#J_HoverShow > tr:nth-child(2) > td:nth-child(1) > span.pay-price > span',
  #  'bid_ladder':'#J_HoverShow > tr:nth-child(1) > td:nth-child(2) > span.pay-price > span',
    'n_register':"em.J_Applyer",
    "n_watch":"#J_Looker",
    'delay_count':'#J_Delay > em',
    
}


Price_info="#J_HoverShow"

PRICE_INFO_dict={
        "reserve_price":"起 拍 价 : (\S*)",
        "bid_ladder":"加价幅度 : (\S*)",
        "evaluation_price":'评 估 价 : (\S*)',
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
col_name=['ID']+list(AUCTION_INFO1.keys())+list(PRICE_INFO_dict.keys())+['incharge_court','lat','lgt','property_name','win_bidder','announce','status']
col_bid =['status','bidder_id','price','date','time']
col_bid2=["ID_info",'status','bidder_id','price','date','time']
location_nav1='#J_DetailTabMenu > li.first > a'
location_nav2='#J_DetailTabMenu > li:nth-child(3) > a'
#location_nav3='#J_DetailTabMenu > li:nth-child(4) > a'
#location_nav4='#J_DetailTabMenu > li:nth-child(5) > a'

location_nav ="#J_DetailTabMenu"

page_load_flag="#sf-foot-2014"

bidding_table='#J_RecordList > tbody'
bidding_next='#J_PageContent > li:nth-child(2) > a'

# it seems I can only run from the ipython 
def open_page(driver,url):
    # only firefox is OK !!! 
    # driver.implicitly_wait(5)
#    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[3]/div[4]/a[7]")))
    try:
        driver.set_page_load_timeout(30)
        driver.get(url)
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'first.current'))
        WebDriverWait(driver, 30).until(element_present)
        time.sleep(5)
    except TimeoutException as ex:
#        check=driver.find_element_by_css_selector(page_load_flag)
#        if not check :
#            print("problem with the page, restart it")
#            driver.quit()
        driver.execute_script("window.stop();")
    
    return driver



def get_info(driver,link_url,status,auction_time_flag):
    '''
    df_info1 : auction info ingeneral
    df_info2 : bidding table
    '''
    
    df_info1=pd.DataFrame(columns=col_name)
    df_info2=pd.DataFrame(columns=col_bid)
    driver=open_page(driver,link_url)
    # df1 for basic infomation
    
    ## get id infomation
    id_info=re.findall(r'\d+',link_url)[0]
    
    # column 1
    candi_info=driver.find_element_by_css_selector(Price_info).text
    for name,ele in PRICE_INFO_dict.items():
        try:
            candi_ele=re.findall(ele,candi_info)[0]
            candi_ele=candi_ele.replace(",","")
            candi_ele=candi_ele.replace("¥","")
            if candi_ele=='':            
                df_info1.loc[0,name]=0
            else:
                df_info1.loc[0,name]=float(candi_ele)
        except:
            pass
        
    try:
        for name,ele in AUCTION_INFO1.items():
            candi_info=driver.find_element_by_css_selector(ele).text
            candi_info=candi_info.replace(",","")
            
            if candi_info=='':            
                df_info1.loc[0,name]=0
            else:
                df_info1.loc[0,name]=float(candi_info)
    except:
        id_info=re.findall(r'\d+',link_url)[0]
        return (df_info1,df_info2,id_info)
    
    
    
    df_info1.loc[0,'finish_time']=driver.find_element_by_css_selector(finish_time).text
    
    tmp_pri=driver.find_element_by_css_selector(priority_info).text.split(":")
    if "无" in tmp_pri[1]: 
        df_info1.loc[0,'priority_people']=0
    else:
        df_info1.loc[0,'priority_people']=1
    
    # column 2
    
    driver.find_element_by_css_selector(location_nav1).click()
    
    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, announce))
    WebDriverWait(driver, 30).until(element_present)
    time.sleep(2)
    
    notice_detail=driver.find_element_by_css_selector(announce).text
    df_info1.loc[0,'announce']=notice_detail
    
    # detail info
    try:
        driver.find_element_by_css_selector(location_nav2).click()
        element_present = EC.presence_of_element_located((By.ID, location))
        WebDriverWait(driver, 30).until(element_present)
        df_info1.loc[0,['lat','lgt']]=driver.find_element_by_id(location).get_attribute("value").split(",")
    except:
        pass
        
    # court information
    df_info1.loc[0,'incharge_court']=driver.find_element_by_xpath("//div[3]/div[2]/div/a[2]").text
    
    check_text=driver.find_element_by_css_selector(location_nav).text.split("\n")
    n_len=len(check_text)
    ii=0
    flag_ii=4
    flag_ii2=3
    while ii<n_len:
        temp_nav=check_text[ii]
        if "竞买" in temp_nav:
            flag_ii=ii+1
        
        if "确认书" in temp_nav:
            flag_ii2=ii+1
        
        ii=ii+1
    
    
    
    

#        df_info1.loc[0,'incharge_court']=driver.find_element_by_class_name(incharge_court).text.split("：")[1]
    
    if "failure" not in status:
    # info2 bidder activity
        
        location_nav3='#J_DetailTabMenu > li:nth-child('+str(flag_ii)+') > a'
        driver.find_element_by_css_selector(location_nav3).click()
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, bidding_table))
        WebDriverWait(driver, 30).until(element_present)
        time.sleep(2)
        flag=1
        if df_info1.loc[0,'priority_people']==1:
            pri_flag=True
            df_pri=pd.DataFrame(columns=['ID','pri_ID'])
            df_pri.loc[0,'ID']=id_info
        else:
            pri_flag=False
        pri_ID=''
        do_search=True
        while flag==1:
            df_temp=pd.DataFrame(columns=col_bid)
            table_content=driver.find_element_by_css_selector(bidding_table).text
            if "出价记录" in table_content:
                break
            
            table_content=table_content.split()
            for j in range(0,int(len(table_content)/5)):
                df_temp.loc[j]=table_content[j*5:j*5+5]
                
                
            df_info2=df_info2.append(df_temp,ignore_index=True)
            driver.find_element_by_css_selector(bidding_table).click()
            
            # find the priority bidder
            if pri_flag==True and do_search == True:
                pri_icon = driver.find_elements_by_class_name('icon-user.icon-priority-1')
                if len(pri_icon)>0:
                    parent_el = pri_icon[0].find_element_by_xpath("..")
                    parent_el=parent_el.find_element_by_xpath("..")
                    pri_ID=parent_el.text
                    df_pri.loc[0,'pri_ID']=pri_ID
                    print('priority bidder! in {} : bidder ID is {}'.format(id_info,pri_ID))
                    con1 = sqlite3.connect(store_path+"auction_pri_house.sqlite")
                    df_pri.to_sql(auction_time_flag, con1, if_exists="append")
                    con1.close()
                    do_search=False
                    
            try:
                driver.find_element_by_css_selector(bidding_next).click()
                time.sleep(0.5)
                driver.execute_script("window.stop();")
            except:
                flag=0
                
                
    

    location_nav4='#J_DetailTabMenu > li:nth-child('+str(flag_ii2)+') > a'            
    check_flag=driver.find_element_by_css_selector(location_nav4).text  
          
    if "确认书" in check_flag:
    # get court name 
        driver.find_element_by_css_selector(location_nav4).click()
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, result))
        WebDriverWait(driver, 30).until(element_present)
        time.sleep(2)
        try:
            res=driver.find_element_by_css_selector(result).text
            df_info1.loc[0,'win_bidder']=re.findall(r'用户姓名(?P<name>.*)通过',res)[0]
        #        df_info1.loc[0,'win_bidder_id']=re.findall(r'通过竞买号(?P<name>.*)于2',res)[0]
            temp=driver.find_element_by_css_selector(property_name).text
            df_info1.loc[0,'property_name']=re.findall(r'标的物名称：(?P<name>.*)',temp)[0]
        except:
            pass
            
                
        
    ## get id infomation
    df_info1.loc[0,'ID']=id_info
    df_info1.loc[0,'status']=status
    # add id info on auction detail
    df_info2["ID_info"]=id_info
    
    return (df_info1,df_info2,id_info)




if __name__ == '__main__':


    
    driver_path="E:\\github\\Project\\web_spider\\land auction taobao\\"


    city=input("input your city ")
    link_path="E:/auction/link/"

    store_path="E:/auction/"
    con = sqlite3.connect(store_path+"auction_info_house.sqlite")
    con2 = sqlite3.connect(store_path+"auction_bidding_house.sqlite")
    df_INFO1=pd.DataFrame(columns=col_name)
    df_INFO2=pd.DataFrame(columns=col_bid2)
#driver=open_page(driver,base_url)
    auction_time_flag=input("input auction time choice: 1- first time, 2- second time ")
    
    df_link=pd.read_csv(link_path+city+"-"+auction_time_flag+"-sf.csv",sep="\t", encoding='utf-8')
#    options = Options()
    profile=webdriver.firefox.firefox_profile.FirefoxProfile()
    # 1 - Allow all images
    # 2 - Block all images
    # 3 - Block 3rd party images 
    profile.set_preference("permissions.default.image", 2)
#    options.set_headless(headless=True)
#    options.add_argument("--headless")
#    options.set_headless(headless=True)
#    driver = webdriver.Firefox(firefox_options=options, executable_path=driver_path)
#    driver=webdriver.Chrome()
    driver=webdriver.Firefox(firefox_profile=profile)
#    driver = webdriver.PhantomJS()
    total_len=len(df_link)
    try:
        for index, row in df_link.iterrows():
            base_url = row["url"]
            status   = row["status"]
            # all I care about is the successful auction
            if status == "done":
                (df_info1,df_info2,id_info)=get_info(driver,base_url,status,auction_time_flag)
            else:
                continue
    
            time.sleep(1)    
            driver.execute_script('window.localStorage.clear();')
        
            df_INFO1=df_INFO1.append(df_info1,ignore_index=True)
            df_INFO2=df_INFO2.append(df_info2,ignore_index=True)
    ## how to save for the data especially for the auction data 
    # http://www.datacarpentry.org/python-ecology-lesson/08-working-with-sql/
            
            if (index+1)% 25 ==0:
                    # output 
                    
                df_INFO1.to_sql(city+"_"+auction_time_flag, con, if_exists="append")
                df_INFO1=pd.DataFrame(columns=col_name)
                df_INFO2.to_sql(city+"_"+auction_time_flag, con2, if_exists="append")
                df_INFO2=pd.DataFrame(columns=col_bid2)
            if (index==total_len-1) and index % 25 !=0:
                df_INFO1.to_sql(city+"_"+auction_time_flag, con, if_exists="append")
                df_INFO2.to_sql(city+"_"+auction_time_flag, con2, if_exists="append")
                df_INFO2=pd.DataFrame(columns=col_bid2)
                df_INFO1=pd.DataFrame(columns=col_name)
            
            print("第-"+str(index)+"-拍卖, 第-"+auction_time_flag+"-次,"+"状态: "+status+" ,"+"id: "+str(id_info))
            
        
        
    except Exception as ex:
        print(ex)
        df_INFO1.to_sql(city+"_"+auction_time_flag, con, if_exists="append")
        df_INFO2.to_sql(city+"_"+auction_time_flag, con2, if_exists="append")
        
    finally:

        # Be sure to close the connection
        con.close()
        con2.close()
#        driver.save_screenshot(link_path+city+"_"+auction_time_flag+"error.png")
#        driver.quit()


