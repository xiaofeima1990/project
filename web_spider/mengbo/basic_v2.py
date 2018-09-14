# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 08:39:50 2018

@author: xiaofeima
basic data webaspider 

"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest, time, re
import pandas as pd 
import numpy as np
import sqlite3
from functools import reduce





url="https://www.crunchbase.com/login"

funding_rounds_url="https://www.crunchbase.com/search/funding_rounds"

# column status add 
COL_name= {
        '"Deal Info"': ['"Funding Stage"','"Pre-Money Valuation"','"Equity Only Funding"'],
        '"Investors"': ['"Number of Investors"','"Number of Partner Investors"'],
        '"Rank & Scores"': ['"CB Rank (Funding Round)"'],
        
        }
cond_choice=[" greater than or equal to ","between","does not equal","equals","less than or equal to", "is blank"]
flag_choice=['"before"','"between"','"after"']


col_name_funding=['Transaction Name',
 'Organization Name',
 'Funding Type',
 'Money Raised',
 'Announced Date',
 'Funding Stage',
 'CB Rank (Funding Round)',
 'Pre-Money Valuation',
 'Equity Only Funding',
 'Number of Investors',
 'Number of Partner Investors',
 'ID',
 'href']


col_name_fund_inv=["num",'Organization/Person Name',
 'Number of Investments',
 'Number of Exits',
 'Location']

col_name_fund_inv2=["num",'Organization/Person Name',
 'Number of Investments',
 'Number of Exits',
 'Location',
 "ID"]

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




def funding_round_setup(driver,url):
    driver = open_page(driver,url)
    column_button=driver.find_element_by_class_name('cb-text-transform-none.flex-none.hide.show-gt-sm.mat-button')
    column_button.click()
    for name, ele in COL_name.items():
        di_button = driver.find_element_by_xpath('//span[contains(text(),'+name+')]')
        di_button.click()
        time.sleep(0.5)
        ad_button = driver.find_element_by_class_name('cb-overflow-ellipsis.flex-nogrow.label')
        for x in ele:
            ad_button.find_element_by_xpath('//span[contains(text(),'+x+')]').click()
        time.sleep(1)
    
    apply_change = driver.find_element_by_class_name("flex-none.layout-row.layout-align-end-center.cb-padding-medium.mat-dialog-actions")
    apply_change.find_element_by_tag_name("button").click() 

    
    return driver


def filter_setup(driver,date1,date2,flag):
    '''
    flag 0 -> before
    flag 1 -> between
    flag 2 -> after
    
    '''
    # create filter 
    fr_search_button = driver.find_element_by_class_name('addFilterButton.queryItemFacet.mat-raised.mat-button')
    fr_search_button.click()
    ## add number of investor filter 
    
    di_button = driver.find_element_by_xpath('//span[contains(text(),"Investors")]')
    di_button.click()
    ad_button = driver.find_element_by_class_name('cb-overflow-ellipsis.flex-nogrow.label').find_element_by_xpath('//span[contains(text(),"Number of Investors")]')
    ad_button.click()
    
    time.sleep(1)
    ## add filter condition greater or equal to 1 for investors 
    driver.find_element_by_class_name("mat-select-value").click()
    range_sel_button1 = driver.find_element_by_xpath('//span[@class="mat-option-text" and contains(text(),"greater than or equal to")]')
    range_sel_button1.click()
    time.sleep(1)
    
    xx=driver.find_element_by_xpath('//input[@placeholder="Enter number e.g. 3"]')
    xx.send_keys("1")    
    time.sleep(1)
    ## add more filters 
    driver.find_element_by_class_name("add-icon.flex-none").click()
    
    # add announcement date 
    di_button = driver.find_element_by_xpath('//span[contains(text(),"Deal Info")]')
    di_button.click()
    time.sleep(1)
    ad_button = driver.find_element_by_class_name('cb-overflow-ellipsis.flex-nogrow.label').find_element_by_xpath('//span[contains(text(),"Announced Date")]')
    ad_button.click()
    time.sleep(1)
    
        
    driver.find_elements_by_class_name("mat-select-value")[1].click()
    time.sleep(1)
    range_sel_button1 = driver.find_element_by_xpath('//span[@class="mat-option-text" and contains(text(),'+flag_choice[flag]+')]')
    time.sleep(1)  
        
    range_sel_button1.click()
    date_input=driver.find_elements_by_xpath("//input[@placeholder='7/18/07, a year ago']")
    time.sleep(1)
    if flag == 1:
        date_input[0].send_keys(date1)
        time.sleep(1)
        date_input[1].send_keys(date2)
    else:
        date_input[0].send_keys(date1)
        
        
    time.sleep(1)
    # search button
    driver.find_element_by_class_name("flex-none.mat-raised-button.mat-accent.ng-star-inserted").click()
    
    return driver

def get_funding_data(driver,count):
    
#    df_funding   = pd.DataFrame(columns=col_name_funding)

    # pick out data 
    table=driver.find_element_by_class_name("grid-container") 
    # all row data 
    rows = table.find_elements_by_class_name("component--grid-row")
#    start = time.clock()
    raw_data_temp=[]
    for i in range(0,len(rows)):
        raw_data=rows[i].text
        raw_data=raw_data.split("\n")
        raw_data.pop(0)
        raw_data.append((count-1)*50+i)
        # when save the data , the next key step is to search for investors 
        num_invetor=rows[i].find_elements_by_class_name("cb-link.component--field-formatter.field-type-integer.ng-star-inserted")[0]
        raw_data.append(num_invetor.get_attribute("href"))
        raw_data_temp=raw_data_temp+raw_data
        if len(raw_data_temp) % 13 !=0:
            input("data spider has problems! PRESS ENTER TO CONTINUE.")
            
#    end = time.clock()
#    print(end-start)
    # save the data into dataframe     
    df_temp_fund=pd.DataFrame(np.array(raw_data_temp).reshape(int(len(raw_data_temp)/13),13),columns=col_name_funding)
    # get the href link data 
#    df_link_data=list(zip(*[df_temp_fund[c].values.tolist() for c in ['href','ID']])) 
    df_link_data=df_temp_fund[['href','ID']].copy()
    return df_temp_fund , df_link_data
    
    




def get_investor_data(driver,df_link_data):
    df_investors = pd.DataFrame(columns=col_name_fund_inv2)
#    df_link_data['ID']=df_link_data.index
    df_link_data=list(zip(*[df_link_data[c].values.tolist() for c in ['href','ID']])) 
    # this part can be converted into parallel programming 
    for ele in df_link_data:
        try:
            driver.get(ele[0])
            
            element_present = EC.presence_of_element_located((By.CLASS_NAME , 'body-wrapper'))
            WebDriverWait(driver, 15).until(element_present)
            time.sleep(0.5)
        except TimeoutException as ex:
            driver.execute_script("window.stop();")
        raw_data=driver.find_element_by_class_name("body-wrapper").text
        rows_data=re.split("\d+\.",raw_data)
        rows_data.pop(0)
        rows_data=reduce(lambda x,y:x+y, rows_data)
        rows_data=rows_data.split("\n")
        rows_data=[item for item in rows_data if item != '']
        
        if len(rows_data) % 4 !=0:
            input("data spider has problems! PRESS ENTER TO CONTINUE.")
            
        
        df_temp_invest=pd.DataFrame(np.array(rows_data).reshape(int(len(rows_data)/4),4),columns=col_name_fund_inv)    
        df_temp_invest["ID"]=ele[1]
        df_investors=df_investors.append(df_temp_invest,ignore_index=True)
        time.sleep(1)
    return df_investors




def get_investor_data2(driver,df_link_data):
    df_investors = pd.DataFrame(columns=col_name_fund_inv2)
#    df_link_data['ID']=df_link_data.index
    df_link_data=list(zip(*[df_link_data[c].values.tolist() for c in ['href','ID']])) 
    # this part can be converted into parallel programming 
    for ele in df_link_data:
        try:
            driver.get(ele[0])
            
            element_present = EC.presence_of_element_located((By.CLASS_NAME , 'body-wrapper'))
            WebDriverWait(driver, 15).until(element_present)
            time.sleep(0.5)
        except TimeoutException as ex:
            driver.execute_script("window.stop();")
            
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
        
    
    
    return df_investors
    




if __name__ == '__main__':

    

    store_path="E:/mengbo/"
    con = sqlite3.connect(store_path+"funding_rounds.sqlite")
    
    flag=input("plese input date filter flag: 0-> before, 1-> between, 2 -> after ")
    date1=input("please input date1 for date filter (before,after this is main date) 'mm/dd/yy' ")
    date2=input("please input date1 for date filter 'mm/dd/yy'")
    flag=int(flag)
    
    driver=webdriver.Firefox()
    driver = open_page(driver,url)
    time.sleep(1)
    driver = funding_round_setup(driver,funding_rounds_url)

    driver2=webdriver.Firefox()
    driver2 = open_page(driver2,url)
    
    


    # deal with the date time 
#    flag=0 # before 
#    date1="01/01/00"
#    date2="01/01/00"
    
    
    
    
    driver = filter_setup(driver,date1,date2,flag)
    time.sleep(1)
    
    
    
    
    df_investors = pd.DataFrame(columns=col_name_fund_inv2)
    df_funding   = pd.DataFrame(columns=col_name_funding)
    df_link_data_t = pd.DataFrame(columns=["href","ID"])
    count_num=1
    while 1:
        start = time.clock()
        df_temp_fund, df_link_data=get_funding_data(driver,count_num)
        end = time.clock()
        print("funding round time consuming is : " + str(end-start))
        n_len=len(df_link_data)
        
        start = time.clock()
        # get_investor_data2 is updated version 
        df_temp_invest=get_investor_data2(driver2, df_link_data)        
        end = time.clock()
        print("related investors time consuming is :" + str(end-start))
        
        df_investors=df_investors.append(df_temp_invest,ignore_index=True)

        df_link_data_t=df_link_data_t.append(df_link_data,ignore_index=True)
        df_funding=df_funding.append(df_temp_fund,ignore_index=True)
    
        if count_num %5 ==0: 
            df_funding.to_sql("funding_round", con, if_exists="append")
            df_investors.to_sql("funding_investors", con, if_exists="append")
            df_link_data_t.to_sql("link_data", con, if_exists="append")
            # refresh the saving df
            df_investors = pd.DataFrame(columns=col_name_fund_inv2)
            df_funding   = pd.DataFrame(columns=col_name_funding)
            df_link_data_t = pd.DataFrame(columns=["href","ID"])
        
        # doing the next page
        next1=driver.find_element_by_class_name("page-button-next.mat-button.mat-primary.ng-star-inserted")
        
        if next1.get_attribute("aria-disabled") == 'false':
            next_url=next1.get_attribute("href")
            try:
                driver.get(next_url)
                
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'page-button-next.mat-button.mat-primary.ng-star-inserted'))
                WebDriverWait(driver, 15).until(element_present)
                time.sleep(0.5)
            except TimeoutException as ex:
                driver.execute_script("window.stop();")
            
            time.sleep(1)
             # stop sign 
        else:
            df_funding.to_sql("funding_round", con, if_exists="append")
            df_investors.to_sql("funding_investors", con, if_exists="append")
            df_link_data_t.to_sql("link_data", con, if_exists="append")
            break



        

        print("current page is "+ str(count_num) + ", data collected: "+ str(count_num*50))
        count_num=count_num+1
    # close the database and driver
    con.close()
    
    driver.quit()
    driver2.quit()
