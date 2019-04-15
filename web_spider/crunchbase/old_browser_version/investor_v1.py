# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 00:08:15 2018

@author: xiaofeima

for investor multiprocessing 
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




col_name_fund_inv=['num','Organization/Person Name',
 'Number of Investments',
 'Number of Exits',
 'Location']


col_name_fund_inv2=['num','Organization/Person Name',
 'Number of Investments',
 'Number of Exits',
 'Location',
 "ID"]


store_path="E:/mengbo/"

def parall_work(work_queue,lock,error_queue,ID):
    
#    driver=webdriver.Ie("IEDriverServer.exe")
    print("start webspider")
    print("queue size is "+str(work_queue.qsize()))
    driver = webdriver.Firefox()
    time.sleep(1)
    while True:
        print("enter while")
        try: 
            if not work_queue.empty():
                print("work queue works")
                link_group=[]
                lock.acquire()
                i=0
                while i<100:
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
                info_get(driver,link_group,lock,ID,error_queue)

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



def info_get(driver,df_link_data,lock,process_ID,error_queue):
    df_investors = pd.DataFrame(columns=col_name_fund_inv2)
    # this part can be converted into parallel programming 
    for ele in df_link_data:
        try:
            driver.get(ele[0])
            
            element_present = EC.presence_of_element_located((By.CLASS_NAME , 'body-wrapper'))
            WebDriverWait(driver, 15).until(element_present)
            time.sleep(0.5)
        except TimeoutException as ex:
            driver.execute_script("window.stop();")
        
        try:
            
            rows=driver.find_elements_by_class_name("component--grid-row")
            raw_data_temp=[]    
            for i in range(0,len(rows)):
                raw_data=rows[i].text
                raw_data=raw_data.split("\n")
                raw_data[0]=raw_data[0].replace(".",'')
                raw_data_temp=raw_data_temp+raw_data
                
    
                if len(raw_data_temp) % 5 !=0:
                    input("data spider has problems! PRESS ENTER TO CONTINUE.")
                 
                
            df_temp_invest=pd.DataFrame(np.array(raw_data_temp).reshape(int(len(raw_data_temp)/5),5),columns=col_name_fund_inv)    
            df_temp_invest["ID"]=ele[1]
            df_investors=df_investors.append(df_temp_invest,ignore_index=True)
            time.sleep(1)
        except:
            print("error for open the webpage ")
            error_queue.put(ele)
            driver.quit()
            time.sleep(5)
            driver=webdriver.Firefox()
            flag=save_data(df_investors,con,lock,process_ID)
            df_investors = pd.DataFrame(columns=col_name_fund_inv2)
            
            
        
    flag=save_data(df_investors,lock,process_ID)


def info_get(driver,df_link_data,lock,process_ID,error_queue):
    



def save_data(df_investors,lock,process_ID):
    try :
        lock.acquire()                    
        
        con2 = sqlite3.connect(store_path+"fund_related_inv.sqlite")
        filename="inv_related_"+str(process_ID)
        df_investors.to_sql(filename, con2, if_exists="append")
        con2.close()
        
        lock.release()
        result=1
        print("successful save "+len(df_investors) +" data")
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
        con = sqlite3.connect(store_path+"funding_rounds.sqlite")
        df_link = pd.read_sql_query("SELECT * from link_data", con)
        print("total number of link data is : " +str(len(df_link)))
        con.close()
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
        
        df_link_data=list(zip(*[df_link[c].values.tolist() for c in ['href','ID']])) 
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
            

