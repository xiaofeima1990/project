# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 21:43:38 2016

@author: xiaofeima
本程序是从搜房土地网上面摘取数据

首先是分类筛选，
筛选完后进行连接的获取，
获取完链接进行信息抓取

错误处理部分想一想，差不多了一共估计也就3000条信息不多


"""


import sys as sys
import codecs,os
import time, re, copy
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import selenium.common.exceptions as S_exceptions
import pandas as pd


'''
地区代码
环渤海 1111111
东北   2222222
长三角 3333333
中西部 4444444
珠三角 5555555

省份代码

北京：110000
天津：120000
河北：130000
山东：370000

辽宁：210000
吉林：220000
黑龙江：230000

上海：310000
江苏：320000
浙江：330000
安徽：340000

重庆：500000
湖北：420000
湖南：430000
陕西：610000
甘肃：620000
青海：630000
宁夏：640000
新疆：650000
山西：140000
内蒙古：150000
江西：360000
河南：410000
广西：450000
四川：510000
贵州：520000
云南：530000

广东：440000
福建：350000
海南：460000


'''
base_url="http://land.fang.com/landfinancing/"
money_select="_______amount_desc_1.html#orderby"
prefix_industry="203_101_0_0_0_0_"

region={'1111111':['110000','120000','130000','370000'],
        '2222222':['210000','220000','230000'],
        '3333333':['310000','320000','330000','340000'],
        '4444444':['500000','420000','430000','610000','620000','630000','640000',
                   '650000','140000','150000','360000','410000','450000','510000',
                   '520000','530000'],
        '5555555':['440000','350000','460000']
        }

error_ID=4


def error_record(type_ID,region_info):
    error_file=open("error_sf_url"+".txt","a+")
    

    temp_record=str(type_ID)+"\t"+str(region_info[0])+"\t"+str(region_info[1])
    temp_record=temp_record+"\t"+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"\n"
    error_file.write(temp_record)
    error_file.close()
    print("error record success")


def open_page(driver,industry_url,region_info,money_select):
    url=industry_url+region_info[0]+"_"+region_info[1]+money_select
    
    driver.get(url)
    # 搜房网一个好处是可以直接url检索，所以也不需要点点点
    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[3]/em")))
#    driver.find_element_by_id("region_1111111").click()
#    driver.find_element_by_id("province_110000").click()
#    driver.find_element_by_id("iItemTypeLandUse_203").click()   
#    driver.find_element_by_id("iTransferFormFinancingForm_101").click()
#    driver.find_element_by_id("order_amount").click()
    total_record=driver.find_element_by_xpath("//div[3]/em").text
    ## 加入 total record 与 总datapage的判断 一页30最多30*100 三千个数据 
    if int(total_record)>3000:
        print('exceed the maximum webspider capacity')
    return driver




def execute_link(driver, i,url):
    flag=3
    count=5
    r_num_link=[]
    while flag != 1:
        try:
            driver.find_element_by_id("pagego").click()
            driver.find_element_by_id("pagego").clear()
            driver.find_element_by_id("pagego").send_keys(str(i))
            driver.find_element_by_link_text("Go").click()            
#            driver.execute_script("QueryAction.GoPage('TAB',"+str(i)+",200)")            
            WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[3]/em")))
            data_check=driver.find_element_by_css_selector("a.cur").text
        except  S_exceptions.InvalidSelectorException as e:
            print(e, "try again")
        except  :
            print("try again strat from beginning-executelink")
            driver=open_page(driver,url)
        
        if data_check == str(i) :
            if len(driver.find_elements_by_xpath("//dl[@id='landlb_B04_22']/dd")):
                num_link=driver.find_elements_by_xpath("//dl[@id='landlb_B04_22']/dd")
                # 加上判断是否有“面议”
                for ele in num_link:
                    if not '面议' in ele.find_element_by_css_selector('b.red_0415 > b.red_0415').text :
                        r_num_link.append(ele.find_element_by_xpath('div[2]/h3/a'))
                        
                flag=1
                
        
        count-=1
        if count==0:
            print("error to get the num_link or next page")
            break
    
        
    
    return (flag,r_num_link)

def catch_url(driver,url,region_info,start_flag=1):
    
    error_ID=4
    
    data_pages=int(driver.find_element_by_xpath("//div[3]/em[2]").text)
    
    
    writeline=''
    file_name='工业用地'
    file_name=".\\url2\\"+file_name+".txt"
    if not os.path.isfile(file_name):
        file_format='w'
    else:
        file_format='a+'
    
    export =codecs.open(file_name,file_format,"utf-8")
        
    ccount=0
    
    ## 想一想错误处理，其实没太复杂的
    try:  
        for i in range(1,data_pages+1):
            (indexflag,num_link)=execute_link(driver, i, url)
#            if indexflag!=1:
#                return (indexflag,driver,temp_date1,temp_date2)
            
            print(i,len(num_link))
            if len(num_link)>0:
                for record in num_link:
                    try:
                        writeline=writeline+record.get_attribute("href")+"\n"
                        ccount +=1
                    except :
                        print("an empty link")
                        error_ID=0
                        error_record(error_ID,region_info)
            
                     
                export.writelines(writeline)
            else:
                print('all the 面议')
                export.close()
                return error_ID
                
        
    
    except (KeyboardInterrupt, SystemExit):
        print("record the error")
        error_ID=3
        
    except :
        print("record the error")
        error_ID=1
    finally:
        if error_ID==1 or error_ID==3:            
            error_record(error_ID,region_info)
            export.writelines(writeline)
            
        export.close()
        return error_ID
# 获取经纬度信息
#driver.execute_script("return pointsAndTypeStr")


    

'''
---------单线程------------

'''


driver = webdriver.Firefox()
industry_url=base_url+prefix_industry
for key , ele in region.items():

    for province in ele:
        region_info=(key,province)
        driver=open_page(driver,industry_url,region_info,money_select)
        result=catch_url(driver,industry_url,region_info,start_flag=1)
        
    