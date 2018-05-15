# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 14:14:22 2016

@author: xiaofeima 

law_spider_recordinfo

这个例子告诉我们，multiprocessing 是不能导入class的！

"""
import os
from law_spider import *
from spider_database import * 
import time
import copy
import multiprocessing as mp
import pandas as pd


href_dict={
"ID_key":"integer primary key",
"href":"text",

}

full_content_info_dict={
"ID_key":"integer primary key",
"full_content":"text",
"title":"text" ,
"data":"text"
}

nav_abs_dict={
"summary":"//div[@id='divTool_Summary']/ul/li/a",
"court":"//div[@id='divTool_Summary']/ul/li/div/div/div[3]/table/tbody/tr/td/a",
"case_type":"//div[@id='divTool_Summary']/ul/li/div/div/div[3]/table/tbody/tr[2]/td/a",
"cause":"//div[@id='divTool_Summary']/ul/li/div/div/div[3]/table/tbody/tr[3]/td/a",
"procedure":"//div[@id='divTool_Summary']/ul/li/div/div/div[3]/table/tbody/tr[4]/td",
"date":"//div[@id='divTool_Summary']/ul/li/div/div/div[3]/table/tbody/tr[5]/td",
"party":"//div[@id='divTool_Summary']/ul/li/div/div/div[3]/table/tbody/tr[6]/td",
"law_info":"//div[@id='divTool_Summary']/ul/li/div/div/div[5]/table/tbody",
"law":"//div[@id='divTool_Summary']/ul/li/div/div/div[5]/table/tbody",
}
summary_nav="//div[3]/table/tbody"
nav_dict={
"title":"//div[@id='contentTitle']",
"date":"//td[@id='tdFBRQ']",
"full_content":"//div[@id='DivContent']",    
}

def recover_info():
    error_info=[]
    if os.path.isfile("error_record_info.txt"):
        fhandle=open("error_record_info.txt",'r')
        for line in fhandle.readlines():
            error_info.append(line)
        fhandle.close()
        
        os.remove('error_record_info.txt')
    else:
        error_info=[]
    
    unfinished_info=[]
    if os.path.isfile("unfinished_record_info.txt"):
        fhandle=open("unfinished_record_info.txt",'r')
        for line in fhandle.readlines():
            unfinished_info.append(line)
        
        fhandle.close()
        os.remove('unfinished_record_info.txt')
        
    else:
        unfinished_info = []
        
    info_list=error_info+unfinished_info
         
    
    return info_list
    
    
def error_save(work_queue,error_queue,flag):
    '''
    flag=1 represent unfinished link
    flag=2 represent error link
    every element in the queue is a dictionary 
    '''
#    filename=str(date_start.year) +"-"+ str(date_start.month)+"_"+str(date_end.year)+"-"+str(date_end.month)
    if flag==1:    
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
    else: 
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
            
def get_page_abs_info(driver,link_data):
    sum_dict={
    "court":"",
    "case_type":"",
    "cause":"",
    "procedure":"",
    "date":"",
    "party":"",
    "ID_key":"",
    }
    sum_dict['ID_key']=link_data['ID_key']
    ##open the link
    print(link_data['href'])
    driver.get(link_data['href'])        
    
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//div[@id='DivContent']")))
    driver.implicitly_wait(3)
    ## open the summary     
    driver.find_element_by_xpath(nav_abs_dict['summary']).click()
    sum_info=driver.find_element_by_xpath(summary_nav)
    ## get the summary info
    for key in sum_dict.keys():
        try: 
            sum_dict[key]=sum_info.find_element_by_xpath(nav_abs_dict[key]).text.strip()
        except:
            sum_dict[key]=""
            
    law_info=driver.find_element_by_xpath(nav_abs_dict['law_info'])
    sum_dict['law']=law_info.find_element_by_xpath(nav_abs_dict['law']).text.strip()
  

    

    sum_dict2={
    "title":"",
    "date2":"",
    "full_content":""        
    }
    for key in sum_dict2.keys():        
        sum_dict2[key]=driver.find_element_by_xpath(nav_dict[key]).text.strip()
    
    sum_dict2['date2']=re.findall("发布日期：(.+)",sum_dict['date'])[0]
    
    sum_dict.update(sum_dict2)
    
    return sum_dict






def parall_work(work_queue,lock,error_queue,ID,db):
    
#    driver=webdriver.Ie("IEDriverServer.exe")
#    driver = webdriver.Firefox()
    driver = webdriver.Chrome("chromedriver.exe")
    print("OK")
    content_list=[]
    while True:
        try: 
            if not work_queue.empty():
                print('ok')
                link = work_queue.get()
                print(link)
    #            lock.acquire()
                print("------"+str(ID)+"sub process is running"+"------")
                dict_content= get_page_abs_info(driver,link)
                
                if dict_content=="":
                    error_queue.put(link)
                if len(content_list)<10 and not work_queue.empty():
                    content_list.append(copy.deepcopy(dict_content))
                else:
                    lock.acquire()
                    db.save_data(content_list)
                    content_list=[]
                    lock.release()
                    
                    
                
    #            work_queue.task_done()           
    #            lock.release()
                
            else:
                print("link is empty")
                driver.close()
                print('close the driver')
                break
        except (KeyboardInterrupt, SystemExit):
            print("interrupt the keyboard")   
        except Exception as ex:
            print("driver error",Exception,":",ex)
            error_queue.put(link)
    
    print('----done----')


#def input_workqueu(work_queue,fele,path):
#    
#    fele=fele.strftime("%Y-X%m").replace('X0','X').replace('X','')
#    fhandle=open(path+str(fele)+'.txt','r')
#    for line in fhandle:
#        work_queue.put(line)
#    fhandle.close()
#    print("input url is done, and delete the url file")
#    try:
#        os.remove(path+fele+'.txt')
#    except Exception as ex:
#        pass


if __name__ == '__main__':
    
    path=".\\"
    
    manager = mp.Manager()
    lock  = manager.Lock()
        
    
    # Establish communication queues
    tasks = manager.Queue()
    error = manager.Queue()
    
    mode_flag=input("recover the error or start new, start new=0, recover=1 ")
    
    if "1" in mode_flag:
        recover_list=recover_info()
        
        for ele in recover_list:
            tasks.put(ele)
                        
            
    else:
        
        flag_data_read=input("get the link data from json(0) or database(1)")
        if int(flag_data_read)==0:
                ## read from json
            link_data=read_link(path,"link-2007")
        else:
            ## read from database
            link_data=[]
            db_link=spider_database('spider_link.db')
            df_link=db_link.read_data(href_dict.keys(),'link')
            for i in range(len(df_link)):
                link_data+=[df_link.loc[i,:].to_dict()]
                
#            print(link_data[1])
                
        for ele in link_data:
            tasks.put(ele)
        if not tasks.empty():
            print('not empty')
        print("data input")  
    num_cpu = mp.cpu_count()
    print('maximum process %s' % num_cpu)
    num_process=input('input the process you want to run')
    num_process=int(num_process)
    pool = mp.Pool(processes=num_process)
    db=spider_database('spider_info.db')
    db.creat_table('content_info',full_content_info_dict)
    print('databse prepared')
    try:
        
        print("start pool")
#        spider_info_list=[]

        for i in range(num_process):
            print(str(i)+" process" )
#            spider_info_list.append(law_spider_info())
            pool.apply_async(parall_work, (tasks,lock,error,i,db))
        
        pool.close()
                
#        parall_work(driver,tasks,lock,error)
        
        pool.join()
        print("pool work is finished")
        print("process is done")
    except (KeyboardInterrupt, SystemExit):
        print("interrupt the keyboard")
    finally:
        print('save the link and info')
        error_save(tasks,error,1)
#        output_error_link(error)
