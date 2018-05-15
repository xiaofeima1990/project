# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 10:50:21 2015
这个程序目的在于进行自动化信息抓取，在读入链接信息后，自动循环抓取信息，主要过程如下：
1. 读取链接数据文档，判断哪些还未爬虫
2. 开始爬虫（单线程），并设置错误记录模式
3. 数据存储，txt格式\t 按月存储



@author: xiaofeima
"""


import sys as sys
import codecs
import time, re
import glob,os,copy
import queue
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import selenium.common.exceptions as S_exceptions
import multiprocessing as mp
import pandas as pd





## error recover saving data format :
# ID start_date end_date num_page num_link time

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


#def error_record(ID,url,url_txt,num_line):
#    error_file=open("error_record_info.txt","a+")
#    
#    temp_record=str(ID)+"\t"+str(num_line)+"\t"+str(url).rstrip()+"\t"+str(url_txt).rstrip()+"\t"
#    temp_record=temp_record+str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))+"\n"
#    error_file.write(temp_record)
#    error_file.close()
#    print("error record success")





list_content=[
        u"行政区",
        u"电子监管号",
        u"项目名称", 
        u"项目位置" ,
        u"面积(公顷)", 
        u"土地来源" ,
        u"土地用途" , 
        u"供地方式" ,  
        u"土地使用年限" ,
        u"行业分类", 
        u"土地级别", 
        u"成交价格(万元)" ,
        u"土地使用权人" , 
        u"约定容积率下限" ,
        u"约定容积率上限", 
        u"约定交地时间" ,
        u"约定开工时间",  
        u"约定竣工时间",
        u"批准单位",
        u"合同签定日期" ]

dic_content={
u"行政区":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c2_ctrl",
u"电子监管号":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl",
u"项目名称":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r17_c2_ctrl", 
u"项目位置":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r16_c2_ctrl" ,
u"面积(公顷)":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl", 
u"土地来源":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c4_ctrl" ,
u"土地用途":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl" , 
u"供地方式": "mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl",  
u"土地使用年限":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c2_ctrl" ,
u"行业分类":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c4_ctrl" , 
u"土地级别":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c2_ctrl" , 
u"成交价格(万元)":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c4_ctrl" ,
u"土地使用权人" :"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9_c2_ctrl", 
u"约定容积率下限":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c4_ctrl" ,
u"约定容积率上限":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c2_ctrl", 
u"约定交地时间" : "mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21_c4_ctrl",
u"约定开工时间": "mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c2_ctrl",  
u"约定竣工时间":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c4_ctrl",
u"批准单位" :"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c2_ctrl",
u"合同签定日期":"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c4_ctrl", 
}



res_name=['stat','c_url','c_file','month']


## main function 

def info_get(driver,link_line,lock):
    
    ## 加入打开存储txt文件的判断工作，以及判断是哪个月的
    ## 加入处理反爬虫电子狗的情况
    
    ## 要不要一次性多进去几个link --不要
    
    result=0
    flag=0
    count=0
    result_df=pd.DataFrame(columns=list_content)
    while flag==0:
        try:
            driver.get(link_line)
            WebDriverWait(driver,60).until(EC.presence_of_element_located((By.ID,"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c4_ctrl")))
            time.sleep(2)
            flag=1
        except Exception as ex:
            print(Exception,":",ex)
            count=count+1
#            if "a70.htm" in str(driver.current_url):
#                driver=login_internet(driver)
#                time.sleep(5)
            if u"安全狗" in str(driver.title):
                print(u"安全狗出现")
                try:                 
                    driver.find_element_by_css_selector("input[type=\"button\"]").click()
                    driver.get(link_line)
                    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.ID,"mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c4_ctrl")))
                    time.sleep(2)
                    flag=1
                except Exception as ex:
                    driver.close()
                    driver = webdriver.Firefox()
#                    driver = webdriver.Ie("IEDriverServer.exe")
                
        # 成功获得信息页面
        if flag==1:
            break
        # 连续打开多次没有成功
        if count>=3:
            print(u"link出错, 存储link ")
            result=0
            return result

    # 信息的抓取
    if count < 3:
        
        temp_list_data={}

        for name, ID_element in dic_content.items():
            try:
                temp_list_data[name]=driver.find_element_by_id(ID_element).text
            except Exception as ex:
                print("read info error",Exception,":",ex)
                temp_list_data[name]=""
            
            print(name, u":", temp_list_data[name] )
            
            
        
        
        result_df.loc[0]=copy.deepcopy(temp_list_data)
        
        p = re.compile(r'\d+')  ## 确定一下是否可行
        temp_date=p.findall(temp_list_data[u'合同签定日期'])
        t_y=temp_date[0]
        t_m=temp_date[1]
        
        try :
            lock.acquire()                    
            filename=".\\info\\"+str(t_y)+'-'+str(t_m)+".csv"
            if not os.path.isfile(filename):
                result_df.to_csv(filename, header ='column_names',sep="\t",index=False)
            else: # else it exists so append without writing the header
                result_df.to_csv(filename, mode = 'a', header=False,sep="\t",index=False)
            lock.release()
            result=1
        except Exception as ex:
            print("write info error",Exception,":",ex)
            result=0
        print(u"<--------------!-------------->")
        
        
    else:
        result=0
        
    
    return result


def parall_work(work_queue,lock,error_queue,ID):
    
#    driver=webdriver.Ie("IEDriverServer.exe")
    driver = webdriver.Firefox()
    while True:
        try: 
            if not work_queue.empty():
                link = work_queue.get()
    #            lock.acquire()
                print("------"+str(ID)+"sub process is running"+"------")
                result=info_get(driver,link,lock)
                if result==0:
                    error_queue.put(link)
    #            work_queue.task_done()           
    #            lock.release()
                
            else:
                print("link is empty")
                driver.close()
                print('close the driver')
                break
            
        except Exception as ex:
            print("write info error",Exception,":",ex)
        
    
    print('----done----')


def input_workqueu(work_queue,fele,path):
    
    fele=fele.strftime("%Y-X%m").replace('X0','X').replace('X','')
    fhandle=open(path+str(fele)+'.txt','r')
    for line in fhandle:
        work_queue.put(line)
    fhandle.close()
    print("input url is done, and delete the url file")
    try:
        os.remove(path+fele+'.txt')
    except Exception as ex:
        pass
    
def output_error_link(error_queue):
#    filename=str(date_start.year) +"-"+ str(date_start.month)+"_"+str(date_end.year)+"-"+str(date_end.month)
    filename="error_record_info.txt"
    if not error_queue.empty():
        
        fhandle=open(filename,'a')
        
        while True:
            if not error_queue.empty():
                url_txt=error_queue.get()
                fhandle.write(str(url_txt).rstrip()+"\n")
            else:
                break
        
        fhandle.close()
        print("save the error link")
    else:
        print("no error link")
    
def error_save(work_queue,error_queue):
#    filename=str(date_start.year) +"-"+ str(date_start.month)+"_"+str(date_end.year)+"-"+str(date_end.month)
    filename="unfinished_record_info.txt" 
    
    if not work_queue.empty():
        fhandle=open(filename,'a')
        while True:
            if not work_queue.empty():
                url_txt=work_queue.get()
                fhandle.write(str(url_txt).rstrip()+"\n")
            else:
                break    
        
        
        
        fhandle.close()
        print("save the link")
    else:
        print('finished')
    
'''
#-------------------------------------------------------
# read the file and input the work queue
#-------------------------------------------------------
'''    

if __name__ == '__main__':
    
    path=".\\url\\"

    wait_file_date=[]
    savefile=[]
    savefile_date=[]
    read_file_list=[]

     
    manager = mp.Manager()
    lock  = manager.Lock()

    read_file_list =os.listdir(path)
    #read_file_list = glob.glob('.\\url\\*.txt')
    print(read_file_list)
    for element in read_file_list:
        savefile.append(os.path.splitext(os.path.basename(element)))
        savefile_date.append(datetime.strptime(os.path.splitext(os.path.basename(element))[0],'%Y-%m'))
        
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
        date_start= input("Please enter query start date (YYYY-M-D,no zeros needed)?")
        date_end=input("Please enter query end date (YYYY-M-D,no zeros needed)?")
        print(date_start,date_end)
        date_start=datetime.strptime( date_start, '%Y-%m-%d')
        date_end=datetime.strptime( date_end, '%Y-%m-%d')
        
        # normal running 
        
        for element in savefile_date:
            if element >=date_start and element <= date_end: 
                wait_file_date.append(element)

    # Establish communication queues
    tasks = manager.Queue()
    error = manager.Queue()
    

    if len(wait_file_date)<1 and 'n' in input_error_recover:
        print("current date range has no new info, please select another one ")
        # wait to continue
    else:
        
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
                    pool.apply_async(parall_work, (tasks,lock,error,i))
                
                pool.close()
                        
        #        parall_work(driver,tasks,lock,error)
                
                pool.join()
                print("pool work is finished")
                print("process is done")
            except (KeyboardInterrupt, SystemExit):
                print("interrupt the keyboard")
            finally:
                print('save the link and info')
                error_save(tasks,error)
                output_error_link(error)

            
            
        else:
            num_cpu = mp.cpu_count()
            print('maximum process %s' % num_cpu)
            num_process=input('input the process you want to run')
            num_process=int(num_process)

            for fele in wait_file_date:
                input_workqueu(tasks,fele,path)
            

                
                pool = mp.Pool(processes=num_process)
                
                
                try:
                    
                    print("start pool")


                        
                    for i in range(num_process):
                        print(str(i)+" process" )
                        pool.apply_async(parall_work, (tasks,lock,error,i))
                    
                    pool.close()
                            
            #        parall_work(driver,tasks,lock,error)
                    
                    pool.join()
                    print("pool work is finished")
                    print("process is done")
                except (KeyboardInterrupt, SystemExit):
                    print("interrupt the keyboard")
                finally:
                    print('save the link and info')
                    error_save(tasks,error)
                    output_error_link(error)
                    
#                for i in range(num_process):
#                    print('close the driver')
#                    drivers[i].close()
    
    