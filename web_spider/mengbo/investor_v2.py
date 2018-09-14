# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 23:46:24 2018

@author: xiaofeima
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

import numpy as np
import sqlite3
from functools import reduce


url="https://www.crunchbase.com/login"




col_name_fund_inv2=["Investor Name", "ID","Transaction Name"]


store_path="E:/mengbo/"



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



def parall_work(work_queue,lock,error_queue,ID):
    
#    driver=webdriver.Ie("IEDriverServer.exe")
    print("start webspider")
    print("queue size is "+str(work_queue.qsize()))
    driver = webdriver.Firefox()
    driver = open_page(driver,url)
    time.sleep(1)
    while True:
        print("enter while")
        try: 
            if not work_queue.empty():
                print("work queue works")
                link_group=[]
                lock.acquire()
                i=0
                while i<50:
                    try:
                        link = work_queue.get()
                        print(link)
                        link_group.append(link)
                    except:
                        print("end of link :" + str(i) )
                        break
                    i+=1
                    
                lock.release()  
    #            lock.acquire()
                print("------"+str(ID)+"sub process is running"+"------")
                info_get2(driver,link_group,lock,ID,error_queue)

    #            work_queue.task_done()           
    #            lock.release()
                
            else:
                print("link is empty")
                driver.close()
                driver.quit()
                print('close the driver')
                break
            
        except Exception as ex:
            print("write info error",Exception,":",ex)
        
    
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
            
#            rows=driver.find_elements_by_class_name("component--grid-row")
            rows=driver.find_element_by_class_name("component--grid-body")
            rows_data=rows.text.split("\n")
            df_temp_invest=pd.DataFrame(np.array(rows_data).reshape(int(len(rows_data)/2),2),columns=["Investor Name","Partner"])
            df_temp_invest.drop("Partner",axis=1,inplace=True)
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
            
    
    
    flag=save_data(df_investors,lock,process_ID)

    



def save_data(df_investors,lock,process_ID):
    try :
        lock.acquire()                    
        
        con2 = sqlite3.connect(store_path+"fund_related_inv.sqlite")
        filename="inv_related_"+str(process_ID)
        df_investors.to_sql(filename, con2, if_exists="append")
        con2.close()
        
        lock.release()
        result=1
        print("successful save "+str(len(df_investors)) +" data")
        df_investors = pd.DataFrame(columns=col_name_fund_inv2)
        
    except Exception as ex:
        print("write info error",Exception,":",ex)
        result=0
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
        df_link=pd.read_csv(store_path+"funding-rounds.csv",encoding="utf-8")
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
        
        try:
            pool = mp.Pool(processes=num_process)
            print("start pool")
            result_v=[]
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
            
#            unfinished_save(tasks)
#            error_link(error)
            

