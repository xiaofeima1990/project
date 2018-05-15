# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 20:18:59 2016

获取搜房网信息


@author: xiaofeima

读取链接
抓取信息
获取gis坐标

"""
import sys as sys
import codecs,os
import time, re, copy,random
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import selenium.common.exceptions as S_exceptions
import pandas as pd


path=".\\url2\\"



info_dict={
    "项目名称":"",
    "更新时间":"",
    "融资金额":"",
    "规划用途":"",
    "使用年限":"",
    "转让形式":"",
    '占地面积':"",
    '建设用地面积':"",
    '规划建筑面积':"",
    "省":"",
    "市":"",
    "联系人":"" ,
    "lat":"",
    "lgt":"",
    "详细信息":""
}

list_content=["项目名称",
    "更新时间",
    "融资金额",
    "规划用途",
    "使用年限",
    "转让形式",
    '占地面积',
    '建设用地面积',
    '规划建筑面积',
    "省",
    "市",
    "联系人",
    "lat",
    "lgt",
    '详细信息']
    
fhandle=open('http.txt','r')
http=fhandle.readlines()
len_http=len(http)
fhandle.close()


def switch_proxy(url):
    count=5    
    flag=0    
    while flag==0 and count>0:   
        profile = webdriver.FirefoxProfile() 
        profile.set_preference("network.proxy.type", 1)
        rand_num=random.randint(0,len_http)
        temp_http=http[rand_num].split('|')
        profile.set_preference("network.proxy.http", temp_http[0])
        profile.set_preference("network.proxy.http_port", temp_http[1].strip())
        profile.update_preferences() 
        driver = webdriver.Firefox(firefox_profile=profile) 
        driver.get(url)
        if not "The page is temporarily unavailable" in driver.title: 
            break
        else:
            count-=1
        
    if count <=0:
        print('please restart the program')
        fhandle=open('unfi_link2.txt','w')
        fhandle.writelines(links)
        fhandle.close()
        exit(1)
    return driver


def catch_info(driver,url,info_dict):
    
    result_df=pd.DataFrame(columns=list_content)
    ## get infomation
    count=5
    flag=0
    while flag==0:    
        try:
            driver.get(url)
           
            WebDriverWait(driver,30).until(EC.presence_of_element_located((By.ID,"landdescribe")))
            time.sleep(1)
            flag=1            
        except Exception as ex:
            print('error open url')        
            print(Exception,":",ex)
            if "The page is temporarily unavailable" in driver.title: 
                print('switch http proxy')
                driver.close()
                driver=switch_proxy(url)
                
        
        count-=1
        
        if count <=0:
            print('error open url stop the program')            
            return (3,driver)

    

        
    try: 
        info=driver.find_element_by_xpath("//div[@id='wrapper']/div[3]/div/div/div[5]").text
        info=info.splitlines()
        for ele in info:
            if "：" in ele:
                key=ele.split('：')[0]
                value=ele.split('：')[1]
                if key in info_dict:
                    info_dict[key]=value
            elif '>' in ele:
                location=ele.split('>')
                info_dict['省']=location[0]
                info_dict['市']=location[1]
            else:
                pass
        
        #time
        update_time=driver.find_element_by_xpath("//div[@id='wrapper']/div[3]/div/div/div[2]/span").text.split("：")
        info_dict[update_time[0]]=update_time[1]
        ## get title
        title=driver.find_element_by_xpath("//div[@id='wrapper']/div[3]/div/div/div").text
        info_dict['项目名称']=title
        ## get specific info
        spe_info=driver.find_element_by_id("landdescribe").text     
        info_dict['详细信息']=spe_info
        
        ## get GIS info the most important part
        gis_info=driver.execute_script("return pointsAndTypeStr")
        if len(gis_info)>0:
            gis_info=gis_info.split('|')[1].split(';')[0].split(',')
            info_dict['lat']=gis_info[0]
            info_dict['lgt']=gis_info[1]
        
        
        result_df.loc[0]=copy.deepcopy(info_dict)
        for key, ele in info_dict.items():
            print(key+':'+ele)
        
        try :                    
            filename=".\\info2\\"+"工业用地.csv"
            if not os.path.isfile(filename):
                result_df.to_csv(filename, header ='column_names',sep="\t",index=False,index=False)
            else: # else it exists so append without writing the header
                result_df.to_csv(filename, mode = 'a', header=False,sep="\t",index=False,index=False)
            
            result=1
        except Exception as ex:
            print("write info error",Exception,":",ex)
            result=0
        print(u"<--------------!-------------->")
    except Exception as ex:
            print('error open url')        
            print(Exception,":",ex)
            if "The page is temporarily unavailable" in driver.title: 
                print('switch http proxy')
                driver.close()
                driver=switch_proxy()
                return (0,driver)
    
    return (result,driver)



fhandle=open(path+'工业用地.txt','r')
links=fhandle.readlines()
fhandle.close()



driver = webdriver.Firefox()
error_link=[]
try:
    while len(links)>0:
        link=links.pop()
        (result,driver)=catch_info(driver,link,info_dict)
        
        if result ==3:
            break
        if result==0:
            error_link.append(link+'\n')
        time.sleep(1)
        
    fhandle=open('unfi_link2.txt','w')
    fhandle.writelines(links)
    fhandle.close()
    
    driver.close()
    
    
    fhandle=open('error_link2.txt','w')
    fhandle.writelines(error_link)
    fhandle.close()
    
except (KeyboardInterrupt, SystemExit):
    print("interrupt the keyboard")
    print('the rest links is ',len(links))
    fhandle=open('unfi_link2.txt','w')
    fhandle.writelines(links)
    fhandle.close()
    
    
        