# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 23:46:24 2018

@author: xiaofeima

操作说明：
1需要改一下
store_path="E:/mengbo/"
改成你存放数据的地方
2 NUM_sel 一次webdriver 一共打开多少个link 20 或者50 或者 100 看block 情况， 我推荐20 或者50 
3 NUM_round 代表经过几轮写入程序库， 要是5 的话代表五轮爬虫才写入， 即若 NUM_sel=20, NUM_round=5 则一次写入100个founding round的link数据
4 ip link 文件可以从 https://free-proxy-list.net/ 获取免费ip 地址 只需要前两列 ip 和 port 用excel整理一下把前两列copy到text文件中
5 想到再说吧~~~ 
List of most active web crawlers User-Agent strings
https://deviceatlas.com/blog/list-of-web-crawlers-user-agents
"""


import sys as sys
import time, re
import os
import queue
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
import selenium.common.exceptions as S_exceptions
import multiprocessing as mp
import pandas as pd
import random
import numpy as np
import sqlite3
from functools import reduce


url="https://www.crunchbase.com/login"




col_name_fund_inv2=["Investor Name", "href","ID","Transaction Name"]

NUM_sel=20    # how many links for each browser
NUM_round = 5 # how many rounds to save 
store_path="E:/mengbo/"


def fake_driver_IP(ip):
    profile = webdriver.FirefoxProfile()
#    profile=webdriver.firefox.firefox_profile.FirefoxProfile()
#    profile.set_preference("general.useragent.override", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")
    ip_address=ip[0]
    ip_port   =ip[1]
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", ip_address)
    profile.set_preference("network.proxy.http_port", int(ip_port))
#    profile.set_preference("network.proxy.ssl", ip_address)
#    profile.set_preference("network.proxy.ssl_port", ip_port)
    profile.set_preference("general.useragent.override","Mozilla/5.0 (compatible; MJ12bot/v1.4.5; http://www.majestic12.co.uk/bot.php?+)")
    profile.set_preference("permissions.default.image", 2)
    profile.update_preferences()    
    driver = webdriver.Firefox(firefox_profile=profile)
    return driver


def fake_driver_usr_agent():
    profile = webdriver.FirefoxProfile()
#    profile=webdriver.firefox.firefox_profile.FirefoxProfile()

#    profile.set_preference("network.proxy.ssl", ip_address)
#    profile.set_preference("network.proxy.ssl_port", ip_port)
    profile.set_preference("general.useragent.override","Mozilla/5.0 (compatible; MJ12bot/v1.4.5; http://www.majestic12.co.uk/bot.php?+)")
    profile.set_preference("permissions.default.image", 2)    
    driver = webdriver.Firefox(firefox_profile=profile)
    return driver
    
    
    
    
    
    





def open_page(driver,url):
    # only firefox is OK !!! 
    # driver.implicitly_wait(5)
#    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[3]/div[4]/a[7]")))
    try:
        driver.set_page_load_timeout(10)
        driver.get(url)
        element_present = EC.presence_of_element_located((By.NAME, 'password'))
        WebDriverWait(driver, 15).until(element_present)
        
        
        if driver.find_element_by_name("password"):
            password=driver.find_element_by_name("password")
            email   =driver.find_element_by_name("email")
            email.send_keys("mbzhangucla@g.ucla.edu")
            password.send_keys("crunchbase_ucla#%&%")
            driver.find_element_by_xpath('//*[@id="mat-tab-content-0-0"]/div/form/div/button[2]').click()
                        
        time.sleep(2)
    except : 
        driver.execute_script("window.stop();")
        print("please check ")
    
    return driver



def parall_work(work_queue,lock,error_queue,ID,IP_list):
    
#    driver=webdriver.Ie("IEDriverServer.exe")
    print("start webspider")
    print("queue size is "+str(work_queue.qsize()))
    time.sleep(1)
    while True:
        print("enter while")
        df_investors = pd.DataFrame(columns=col_name_fund_inv2)
        kk=0
        try: 
            if not work_queue.empty():
                print("work queue works")
                link_group=[]
                lock.acquire()
                ip_t=random.choice(IP_list)
                ip_t=ip_t.split()
                driver = fake_driver_IP(ip_t)
                i=0
                while i<NUM_sel:
                    try:

                        
                        link = work_queue.get()
                        
                        link_group.append(link)
                    except:
                        print("end of link :" + str(i) )
                        break
                    i+=1
                    
                lock.release()  
    #            lock.acquire()
                print("------"+str(ID)+"sub process is running"+"------")
                df_investors=df_investors.append(info_get2(driver,link_group,lock,ID,error_queue),ignore_index=True)
                print(str(NUM_sel)+" successful")
                driver.quit()
                kk+=1
                
                if kk % NUM_round == 0 :
                    lock.acquire()
                    flag=save_data(df_investors,lock,ID)
                    df_investors = pd.DataFrame(columns=col_name_fund_inv2)
                    lock.release() 
                
                    
    #            work_queue.task_done()           
    #            lock.release()
                
            else:
                print("link is empty")
                lock.acquire()
                flag=save_data(df_investors,lock,ID)
                lock.release()
                driver.close()
                driver.quit()
                print('close the driver')
                break
            
        except Exception as ex:
            print("write info error",Exception,":",ex)
            lock.acquire()
            flag=save_data(df_investors,lock,ID)
            lock.release()
    
    print('----done----')
    return ID



def info_get2(driver,df_link_data,lock,process_ID,error_queue):
    df_investors = pd.DataFrame(columns=col_name_fund_inv2)
    for ele in df_link_data:
        try:

                        
            driver.get(ele[0]+"/investors/investors_list#section-investors")
            element_present = EC.presence_of_element_located((By.CLASS_NAME , 'component--list-card'))
            WebDriverWait(driver, 15).until(element_present)
            time.sleep(0.5)
        except TimeoutException as ex:
            driver.execute_script("window.stop();")
        try:
            
            rows=driver.find_elements_by_class_name("component--grid-row")
            rows_data=[]
            for i in range(0,len(rows)):
                temp_name=rows[i].find_element_by_class_name("flex-no-grow.cb-overflow-ellipsis.identifier-label").text
                rows_data.append(temp_name)
                temp_href=rows[i].find_element_by_class_name("cb-link.layout-row.layout-align-start-center.ng-star-inserted")
                rows_data.append(temp_href.get_attribute("href"))
                if len(rows_data) % 2 !=0:
                        print("data spider has problems!")
            
            
            df_temp_invest=pd.DataFrame(np.array(rows_data).reshape(int(len(rows_data)/2),2),columns=["Investor Name","href"])
            df_temp_invest["ID"]=ele[1]
            df_temp_invest["Transaction Name"]=ele[2]
            df_investors=df_investors.append(df_temp_invest,ignore_index=True)
            time.sleep(1)
        except:
            print("error for open the webpage ")
            error_queue.put(ele)
            driver.quit()
            time.sleep(5)
            driver=webdriver.Firefox()
            flag=save_data(df_investors,lock,process_ID)
            df_investors = pd.DataFrame(columns=col_name_fund_inv2)
            
    
    return df_investors


def save_data(df_investors,lock,process_ID):
    lock.acquire() 
    try :
                              
        con2 = sqlite3.connect(store_path+"fund_related_inv.sqlite")
        filename="inv_related_"+str(process_ID)
        print(df_investors)
        df_investors.to_sql(filename, con2, if_exists="append")
        con2.close()
        result=1
        print("successful save "+str(len(df_investors)) +" data")
        
    except Exception as ex:
        print("write info error",Exception,":",ex)
        result=0
    lock.release()
    print(u"<--------------!-------------->")
    return result
    
    
def unfinished_save(work_queue):
#    filename=str(date_start.year) +"-"+ str(date_start.month)+"_"+str(date_end.year)+"-"+str(date_end.month)
    filename="unfinished_record_info.txt" 
    
    if not work_queue.empty():
        fhandle=open(filename,'a')
        while True:
            if not work_queue.empty():
                url_txt=work_queue.get()
                fhandle.write(str(url_txt)+"\n")
            else:
                break    
        
        
        
        fhandle.close()
        print("save the link")
    else:
        print('finished')
        
def error_link(error_queue):
#    filename=str(date_start.year) +"-"+ str(date_start.month)+"_"+str(date_end.year)+"-"+str(date_end.month)
    filename="error_record_info.txt"
    if not error_queue.empty():
        
        fhandle=open(filename,'a')
        
        while True:
            if not error_queue.empty():
                url_txt=error_queue.get()
                fhandle.write(str(url_txt)+"\n")
            else:
                break
        
        fhandle.close()
        print("save the error link")
    else:
        print("no error link")
    
def recover_info():
    
    if os.path.isfile("error_record_info.txt"):
        fhandle=open("error_record_info.txt",'r')
        error_info = fhandle.readlines()
        fhandle.close()
        
        os.remove('error_record_info.txt')
    else:
        error_info=None
    
    if os.path.isfile("unfinished_record_info.txt"):
        fhandle=open("unfinished_record_info.txt",'r')
        unfinished_info = fhandle.readlines()
        fhandle.close()
        os.remove('unfinished_record_info.txt')
        
    else:
        unfinished_info=None
    
    return (error_info, unfinished_info)


result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)

    
'''
#-------------------------------------------------------
# read the file and input the work queue
#-------------------------------------------------------
'''    

if __name__ == '__main__':
    
    

    wait_file_date=[]
    savefile=[]
    savefile_date=[]
    read_file_list=[]

     
    manager = mp.Manager()
    lock  = manager.Lock()
    
    
    
#    date_start=input("Please enter query start date (YYYY-M-D,no zeros needed)?")
#    date_end=input("Please enter query end date (YYYY-M-D,no zeros needed)?")
#    date_start=datetime.strptime( date_start, '%Y-%m-%d')
#    date_end=datetime.strptime( date_end, '%Y-%m-%d')
    
    input_error_recover=input("start infor getting error recover not or yes ")
    if 'y' in input_error_recover:
        (error_info,unfinish_info)=recover_info()
        if error_info is None and unfinish_info is None :
            print("no error info, please restart ")
            exit(1)
            
    else:
        df_link=pd.read_csv(store_path+"funding-rounds.csv",encoding="GBK")
#        df_link=pd.read_csv(store_path+"funding-rounds.txt",sep="\t",encoding="utf-8")
        df_link['ID']=df_link.index
        df_link=df_link.rename(columns={"Transaction Name URL": "href"})
        print("total number of link data is : " +str(len(df_link)))
        
#        date_start=datetime.strptime( date_start, '%Y-%m-%d')
#        date_end=datetime.strptime( date_end, '%Y-%m-%d')
        

    # Establish communication queues
    tasks = manager.Queue()
    error = manager.Queue()
    


    
    if 'y' in input_error_recover:
        if not error_info is None:
            
            for ele in error_info:
                tasks.put(ele)
        
        if not  unfinish_info is None:    
            for ele in unfinish_info:
                tasks.put(ele)

            
        num_cpu = mp.cpu_count()
        print('maximum process %s' % num_cpu)
        num_process=input('input the process you want to run')
        num_process=int(num_process)
        pool = mp.Pool(processes=num_process)
        
        
        try:
            
            print("start pool")
            
            for i in range(num_process):
                print(str(i)+" process" )
                pool.apply_async(parall_work, args=(tasks,lock,error,i),callback = log_result)
                
            pool.close()
            
    #        parall_work(driver,tasks,lock,error)
            
            pool.join()
            print("pool work is finished")
            print("process is done")
        except (KeyboardInterrupt, SystemExit):
            print("interrupt the keyboard")
        finally:
            print('save the link and info')
            unfinished_save(tasks)
            error_link(error)

        
        
    else:
        num_cpu = mp.cpu_count()
        print('maximum process %s' % num_cpu)
        num_process=input('input the process you want to run')
        num_process=int(num_process)
        
        df_link_data=list(zip(*[df_link[c].values.tolist() for c in ['href','ID',"Transaction Name"]])) 
        for link in df_link_data:
            tasks.put(link)
        
        fn=open("ip_list.txt",'r')
        IP_list=fn.readlines()
        fn.close()
        
        try:
            pool = mp.Pool(processes=num_process)
            print("start pool")
            result_v=[]
            for i in range(num_process):
                print(str(i)+" process" )
                pool.apply_async(parall_work, args=(tasks,lock,error,i,IP_list),callback = log_result)
                
                
            pool.close()
                    
    #        parall_work(driver,tasks,lock,error)
            
            pool.join()
            print("pool work is finished")
            print("process is done")
        except (KeyboardInterrupt, SystemExit):
            print("interrupt the keyboard")
        finally:
            print('save the link and info')
            
#            unfinished_save(tasks)
#            error_link(error)
            

