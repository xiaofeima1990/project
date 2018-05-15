
# coding: utf-8
'''
# # 土地一级市场数据抓取(1)
# 
# 本程序在于土地一级市场交易数据的抓取，数据抓取分为二个部分：
# 
# 1. 获取成交信息的相关链接
# 2. 定位信息并抓取信息
# 
# 本程序主要集中解决第一部分的任务，获取相关网址的url链接并存储

# 
# * 网址： [土地市场网](www.landchina.com) www.landchina.com
# * python 版本： Python3.4
# * 所需模块： selenium(支持py2,3 !)
# 

# 错误恢复： 把错误信息存储成表格形式，统一恢复，直接在最开始运行的时候选择yes 就可自动运行错误信息
# ## IE 版本（稳定版）
'''
# In[1]:

import sys as sys
import codecs,os
import time, re
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import selenium.common.exceptions as S_exceptions
import pandas as pd
import multiprocessing as mp
# driver = webdriver.Firefox()

'''
# 修改，把错误恢复变成表格形式进行或者以csv形式存储或者以table形式存储
# record error information 
error_ID= 0 # record error ID type number ==0 is empty link ==1 is error and exist
## error recover saving data format :
# ID start_date end_date num_page num_link time
'''

error_ID=-1

def error_record(type_ID,start_date,end_date,num_page,ccount):
    error_file=open("error_record_url"+".txt","a+")
    
    start_date=start_date.strftime("%Y-%m-%d")
    end_date=end_date.strftime("%Y-%m-%d")
    temp_record=str(type_ID)+"\t"+str(start_date)+"\t"+str(end_date)+"\t"+str(num_page)+"\t"+str(ccount)
    temp_record=temp_record+"\t"+str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))+"\n"
    error_file.write(temp_record)
    error_file.close()
    print("error record success")

def error_recover():
    error_info=pd.read_csv("error_record_url.txt",sep='\t',header=None)
    os.remove('error_record_url.txt')          
    return error_info



def begin_input():
    fflag=0
    while (fflag==0):
        error_flag=input( "make a choice : error recover: yes or not ")
        #     print("this is datetime format", date_start.strftime("%Y-X%m").replace('X0','X').replace('X',''))
        #     print("this is datetime format", date_start.strftime("%Y-X%m-X%d").replace('X0','X').replace('X',''))
        if "n" in error_flag:
            date_start= input("Please enter start date (YYYY-M-D,no zeros needed)")
            date_end=input("Please enter end date (YYYY-M-D,no zeros needed),or leave it none when you want today")
            if date_start :
                date_start=datetime.strptime( date_start, '%Y-%m-%d')
                if date_start:
                    date_end=datetime.strptime( date_end, '%Y-%m-%d')
                else :
                    date_end=datetime.today()
                if date_start>date_end or date_start>datetime.today():
                    print('error! reinput the correct date!')
                else :
                    fflag=1
                    print("start date", date_start.strftime("%Y-X%m-X%d").replace('X0','X').replace('X',''))
                    print("end   date", date_end.strftime("%Y-X%m-X%d").replace('X0','X').replace('X',''))
            else:
                print("start date can not be empty")
        else:
            print("error recover processing")
            error_info=error_recover()
            break
            
    if "n" in error_flag:
        return (error_flag,date_start,date_end)
    else:
        return (error_flag,error_info)


def open_page(driver,url,temp_date1,temp_date2):
    driver.get(url)
    # driver.implicitly_wait(10)
    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.CSS_SELECTOR,"td.pager")))
    driver.find_element_by_id("TAB_QueryConditionItem270").click()
    driver.find_element_by_id("TAB_queryDateItem_270_1").click()
    driver.find_element_by_link_text(u"×").click()
    driver.find_element_by_id("TAB_queryDateItem_270_1").send_keys(temp_date1.strftime("%Y-X%m-X%d").replace('X0','X').replace('X',''))
    driver.find_element_by_id("TAB_queryDateItem_270_2").click()
    driver.find_element_by_link_text(u"×").click()
    driver.find_element_by_id("TAB_queryDateItem_270_2").send_keys(temp_date2.strftime("%Y-X%m-X%d").replace('X0','X').replace('X',''))
    driver.find_element_by_id("TAB_QueryButtonControl").click()
    return driver



def makesure_page(driver,url,temp_date1,temp_date2,try_times=4):
    index_flag=1
    while (try_times > 0):
        driver=open_page(driver,url,temp_date1,temp_date2)
        time.sleep(3)
        try_times=try_times-1
        try:
            WebDriverWait(driver,60).until(EC.presence_of_element_located((By.CSS_SELECTOR,"td.pager > span")))
            index_flag=0

            if len(driver.find_elements_by_xpath("//*[contains(text(), '没有检索到相关数据')]"))> 0:
                print("the starting date need to set earlier ")
                index_flag=2

        except S_exceptions.ErrorInResponseException as e:
            index_flag=1
            print("No response please try again, make sure you connect the Internet ")

        except Exception as e :
            index_flag=1
            print("Unexpected error: %s" %e)
            print("open new driver")
            driver.close()
            driver = webdriver.Ie("IEDriverserver.exe")
            
        if index_flag==0 :
            print( "page succeed")
            break

        if try_times==0 :
            print("fatal error, can't connect to Landchina.com,Please try again later")
            index_flag=3
            break
    return (index_flag,driver)
# index_flag==0 succeed ==3 internet error ==2 没有相关数据



def execute_link(driver, i, check_flag,url,temp_date1,temp_date2):
    flag=3
    count=5
    while flag != 1:
        try:
            driver.find_element_by_css_selector("td.pager > input[type=\"text\"]").clear()
            driver.find_element_by_css_selector("td.pager > input[type=\"text\"]").send_keys(str(i))
            driver.find_element_by_css_selector("td.pager > input[type=\"button\"]").click()            
#            driver.execute_script("QueryAction.GoPage('TAB',"+str(i)+",200)")            
            WebDriverWait(driver,60).until(EC.presence_of_element_located((By.CSS_SELECTOR,"td.pager")))
            if i >10:             
                data_check=driver.find_element_by_xpath("//td[@id='mainModuleContainer_485_1113_1539_tdExtendProContainer']/table/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[2]/span[2]").text
            else:
                data_check=driver.find_element_by_xpath("//td[@id='mainModuleContainer_485_1113_1539_tdExtendProContainer']/table/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[2]/span").text
        except  S_exceptions.InvalidSelectorException as e:
            print(e, "try again")
        except  :
            print("try again strat from beginning-executelink")
            (index_flag,driver)=makesure_page(driver,url,temp_date1,temp_date2)
            if index_flag !=0:
                num_link=0
                flag=index_flag
                break
            
        
        if data_check == str(i) :
            if len(driver.find_elements_by_xpath("/html/body/form/font/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/a")):
                num_link=driver.find_elements_by_xpath("/html/body/form/font/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/a")
                flag=1
        
        count-=1
        if count==0:
            print("error to get the num_link or next page")
            break
            
    return (flag,num_link)

# flag ==1 is ok ortherwise is not ok 



def catch_url(driver, url, temp_date1, temp_date2,date_end,error_flag, start_point=1):
    '''
    这里temp_date1 和 tempdate2 应当是同一个月的日期才行
    '''
    global error_ID
    start_flag=0
    if "y" in error_flag[0]:
        start_point=error_flag[1]
        start_flag=1
        
    
    while (temp_date2 <= date_end):
        
        data_confirm="n"
        while data_confirm != "y":

            (indexflag,driver)=makesure_page(driver,url,temp_date1,temp_date2)
            if indexflag!=0:  # 3 internet failed  2 网页还没更新到这么快
                return (indexflag,driver,temp_date1, temp_date2)


            flag=0
            while flag==0:
                try: 
                    data_summary=driver.find_element_by_css_selector("td.pager").text
                    flag=1
                    print("get the info")
                except :
                    print("error in finding element")
            
            
            print("-------"+data_summary+"------")
            page_info=re.findall("[-+]?\d+[\.]?\d*", data_summary)
            num_page= page_info[0]
            total_record=page_info[-1]
            # check the number of pages 
            if int(num_page) <= 200:
                data_confirm ="y"
            else :
                interval=temp_date2-temp_date1
                temp_date2=temp_date2-timedelta(days=int(interval.days)/2)
                print('seperate the interval')
                if temp_date2<temp_date1 :
                    print("error, the information is too big, we need to start with day by day ")
                    temp_date2=temp_date1+timedelta(days=1)

        #------------------------------------------------------------------------------------------------------------------------------------------#
        # next part is to scrap the url link 
        #------------------------------------------------------------------------------------------------------------------------------------------#
        print("current date range is :",str(temp_date1)+"---"+str(temp_date2))
        data_pages=int(data_summary[data_summary.index(u'共')+1:data_summary.index(u'页')])
        #         file_name =temp_date1.strftime("%Y-X%m-X%d").replace('X0','X').replace('X','')
        file_name=str(temp_date1.year)+'-'+str(temp_date1.month)
        file_name=".\\url\\"+file_name+".txt"
        if not os.path.isfile(file_name):
            file_format='w'
        else:
            file_format='a+'
        
        export =codecs.open(file_name,file_format,"utf-8")
        
        ccount=0
        try:  
            for i in range(start_point,data_pages+1):
                (indexflag,num_link)=execute_link(driver, i, data_summary,url,temp_date1,temp_date2)
                if indexflag!=1:
                    return (indexflag,driver,temp_date1,temp_date2)
                
                print(i,len(num_link))
                time.sleep(1)
                
                ccount=0
                writeline=''
                if start_flag==1:
                    start_flag=0
                    ccount=error_flag[2]
                    for x in range(error_flag[2],len(num_link)+1):
                        try:
                            writeline=writeline+num_link[x].get_attribute("href")+"\n"
                            ccount +=1
                        except :
                            print("an empty link")
                            error_record(error_ID, temp_date1, temp_date2,i,ccount+1)
                    
                    if (error_flag[3]==0):
                        export.writelines(writeline)
                        
                        break
                else:
                    
                    for record in num_link:
                        try:
                            writeline=writeline+record.get_attribute("href")+"\n"
                            ccount +=1
                        except :
                            print("an empty link")
                            error_ID=0
                            error_record(error_ID, temp_date1, temp_date2,i,ccount+1)
                
                     
                export.writelines(writeline)
                
        
        except (KeyboardInterrupt, SystemExit):
            print("record the error")
            error_ID=3
            
        except :
            print("record the error")
            error_ID=1
        finally:
            if error_ID==1 or error_ID==3:            
                error_record(error_ID, temp_date1, temp_date2,i,ccount+1)
                export.writelines(writeline)
                
            export.close()
#            e_email.send_mail("error in catching url!","an error happens")
                # driver.close()    

        
    #------------------------------------------------------------------------------------------------------------------------------------------#    
        # judge the time period
        temp_date1 = temp_date2 + timedelta(days=1)
        temp_date2 = temp_date1 + timedelta(days=10)
        ## consistent within month 
        t_m  = temp_date1.month
        t_m2 = temp_date2.month
        if t_m2!=t_m :
            if t_m+1 <=12:
                temp_date2=datetime(temp_date1.year,t_m+1,1)-timedelta(days=1)
            else:
                temp_date2=datetime(temp_date1.year,12,31)
        
        if temp_date1 <= date_end and temp_date2 > date_end:
            temp_date2=date_end
        
    driver.close()
    
    return (1,)




'''
-------------------------------------------------------------------------------

'''

## 单线程操作
url ="http://www.landchina.com/default.aspx?tabid=263&ComName=default"
driver = webdriver.Ie("IEDriverserver.exe")
#driver = webdriver.Firefox()
input_info=begin_input()
if len(input_info)==2:
    (error_flag,error_info)= input_info
    (ncow,ncol)=error_info.shape
    for x in range(0,ncow,1):
        (ID,date_start,date_end,num_page,num_link,Time)=error_info.loc[x,:]
        date_start = datetime.strptime( date_start, '%Y-%m-%d')
        date_end   = datetime.strptime( date_end, '%Y-%m-%d')
        error_sub_info=('y',num_page,num_link,ID)
        
        run_flag=0
        while run_flag==0:
            result_info=catch_url(driver, url, date_start, date_end,date_end,error_sub_info)
            if len(result_info)<2:
                run_flag=1
            else:
                if result_info[0]==2:  # 2 网页还没更新到这么快
                    print("the website has not update yet")
                    run_flag=1
                else: 
                    ## test the internet
                    ## the result_info has (indexflag,driver,temp_date1,temp_date2)
                    pass
    

        
    
    
else:        
    (error_flag, date_start,date_end) = input_info
    error_sub_info=('n',)

    total_days=date_end - date_start
    total_days=int(total_days.days)+1
    print("total date range :  %s -- %s", (date_start,date_end))
    print("total days: %s" %str(total_days))
    
    
    temp_date1=date_start
    
    temp_date2=temp_date1+ timedelta(days=10)
    if temp_date2 > date_end:
        temp_date2=date_end
  
##划分 data time 
    run_flag=0
    while run_flag==0:
        result_info=catch_url(driver, url, temp_date1, temp_date2,date_end,error_sub_info)
        if len(result_info)<2:
            run_flag=1
        else:
            if result_info[0]==2:  # 2 网页还没更新到这么快
                print("the website has not update yet")
                run_flag=1
            else: 
                ## test the internet
                ## the result_info has (indexflag,driver,temp_date1,temp_date2)
                pass
    


#e_email.send_mail("finish and succeed", "The program is ok for you")




#### 进程池操作
##
#def parallel_work(ID,url,temp_date1,temp_date2,date_end,error_sub_info):
#    print("ID: %d" % ID)
#    driver = webdriver.Ie("IEDriverserver.exe")
#    catch_url(driver, url, temp_date1, temp_date2, date_end,error_sub_info)
#    print("end of process %s" % os.getpid())
##
#if __name__ == "__main__":
#    url="http://www.landchina.com/default.aspx?tabid=263&ComName=default"
#    driver = webdriver.Ie("IEDriverserver.exe")
#    
#    total_days=date_end - date_start
#    total_days=int(total_days.days)+1
#    print("total date range :  %s--%s", (date_start,date_end))
#    print("total days: %s" %str(total_days))
#    
#    split_num=int(total_days/30)+1
#    
#    pool = multiprocessing.Pool(processes = 3)
#    for i in range(split_num):
#        temp_date1=date_start+i*30
#        if temp_date1>date_end:
#            break
#        temp_date2=temp_date1+ timedelta(days=10)
#        temp_date3=date_start+(i+1)*30
#        if temp_date2 > date_end:
#            temp_date2=date_end
#        if temp_date3 > date_end:
#            temp_date3=date_end
#        pool.apply_async(func, (i,driver, url, temp_date1, temp_date2, temp_date3))   #维持执行的进程总数为processes=3，当一个进程执行完毕后会添加新的进程进去
#        temp_date1+=1
#    print("starting the pool !!!")
#    
#    pool.close()
#    pool.join()   
#    #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
#
#    print("Sub-process(es) done.")
#




