# -*- coding: utf-8 -*-
"""
Created on Sun Jul  1 16:33:15 2018

@author: xiaofeima

for mengbo webspider 
https://www.crunchbase.com

scrap all the companies and investors information from the website

"""



'''
steps:
1 login the web
2 funding rounds (with full column info)
3 deal with filter and download the data 
4 find investors and connected to the original data 




'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import pandas as pd 
import numpy as np
import sqlite3


store_path="E:/mengbo/"
con = sqlite3.connect(store_path+"funding_rounds.sqlite")
con2 = sqlite3.connect(store_path+"investors_related.sqlite")



def open_page(driver,url):
    # only firefox is OK !!! 
    # driver.implicitly_wait(5)
#    WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[3]/div[4]/a[7]")))
    try:
        driver.set_page_load_timeout(10)
        driver.get(url)
        if driver.find_element_by_name("password"):
            password=driver.find_element_by_name("password")
            email   =driver.find_element_by_name("email")
            email.send_keys("mbzhangucla@g.ucla.edu")
            password.send_keys("crunchbase_ucla#%&%")
            driver.find_element_by_xpath('//*[@id="mat-tab-content-0-0"]/div/form/div/button[2]').click()
                        
                               
    except : 
        print("unable to open the webpage successfully")
    
    return driver


driver=webdriver.Firefox()


url="https://www.crunchbase.com/login"

funding_rounds="https://www.crunchbase.com/search/funding_rounds"

driver = open_page(driver,funding_rounds)


# column status add 
COL_name= {
        "Deal Info": ["Funding Stage","Pre-Money Valuation","Equity Only Funding"],
        "Investors": ["Number of Investors","Number of Partner Investors"],
        "Rank & Scores": ["CB Rank (Funding Round)"],
        
        }

for name, ele in COL_name.items():
    di_button = driver.find_element_by_xpath('//span[contains(text(),'+name+')]')
    di_button.click()
    ad_button = driver.find_element_by_class_name('cb-overflow-ellipsis.flex-nogrow.label')
    for x in ele:
        ad_button.find_element_by_xpath('//span[contains(text(),'+COL_name[x]+')]').click()
    time.sleep(1)
    
apply_change = driver.find_element_by_class_name("flex-none.layout-row.layout-align-end-center.cb-padding-medium.mat-dialog-actions")
apply_change.find_element_by_tag_name("button").click() 

fr_search_button = driver.find_element_by_class_name('addFilterButton.queryItemFacet.mat-raised.mat-button')
fr_search_button.click()


# create filter 
## add number of investor filter 
di_button = driver.find_element_by_xpath('//span[contains(text(),"Investors")]')
di_button.click()
ad_button = driver.find_element_by_class_name('cb-overflow-ellipsis.flex-nogrow.label').find_element_by_xpath('//span[contains(text(),"Number of Investors")]')
ad_button.click()


## add filter condition greater or equal ... 
driver.find_element_by_class_name("mat-select-value").click()
cond_choice=[" greater than or equal to ","between","does not equal","equals","less than or equal to", "is blank"]
range_sel_button1 = driver.find_element_by_xpath('//span[@class="mat-option-text" and contains(text(),"equals")]')
range_sel_button1.click()
xx=driver.find_elements_by_class_name("mat-form-field-infix")
xx[2].send_keys("1")

## add more filters 
driver.find_element_by_class_name("add-icon.flex-none").click()

# add announcement date 
di_button = driver.find_element_by_xpath('//span[contains(text(),"Deal Info")]')
di_button.click()
ad_button = driver.find_element_by_class_name('cb-overflow-ellipsis.flex-nogrow.label').find_element_by_xpath('//span[contains(text(),"Announced Date")]')
ad_button.click()


driver.find_elements_by_class_name("mat-select-value")[1].click()
range_sel_button1 = driver.find_element_by_xpath('//span[@class="mat-option-text" and contains(text(),"between")]')
range_sel_button1.click()
date_input=driver.find_elements_by_xpath("//input[@placeholder='7/18/07, a year ago']")
date_input[0].send_keys("01/01/00")
date_input[1].send_keys("02/01/00")

# search button
driver.find_element_by_class_name("flex-none.mat-raised-button.mat-accent.ng-star-inserted").click()




# pick out data 
table=driver.find_element_by_class_name("grid-container")
# column name 
col_name=table.find_element_by_class_name("component--grid-header").text
col_name=col_name.split("\n")
col_name.append("ID")
col_name.append("href")

col_name2=["Organization/Person Name",'Number of Investments','Number of Exits','Location']
df_funding   = pd.DataFrame(columns=col_name)
df_investors = pd.DataFrame(columns=col_name2)

# row data 
rows = table.find_elements_by_class_name("component--grid-row")
start = time.clock()
count=0
raw_data_temp=[]
for i in range(0,len(rows)):
    raw_data=rows[i].text
    raw_data=raw_data.split("\n")
    raw_data.pop(0)
    raw_data.append(count*50+i)
    # when save the data , the next key step is to search for investors 
    num_invetor=rows[i].find_elements_by_class_name("cb-link.component--field-formatter.field-type-integer.ng-star-inserted")[1]
    raw_data.append(num_invetor.get_attribute("href"))
    raw_data_temp=raw_data_temp+raw_data
end = time.clock()
print(end-start)    
df_temp_fund=pd.DataFrame(np.array(raw_data_temp).reshape(50,13),columns=col_name)    
df_funding=df_funding.append(df_temp_fund,ignore_index=True)

# doing the next page
next1=driver.find_element_by_class_name("page-button-next.mat-button.mat-primary.ng-star-inserted")
next_url=next1.get_attribute("href")
driver.get(next_url)

   
#start = time.clock()
#rows_data=driver.find_element_by_class_name("component--grid-body").text
#end = time.clock()

# save the data into sqlite3
df_funding.to_sql("funding_round", con, if_exists="append")


'''
get investors info 

'''
from functools import reduce
# get the url link 
investor_link=df_funding['href'].tolist()
fund_ID=df_funding['ID'].tolist()
invest_url=tuple(zip(investor_link,fund_ID))

for ele in invest_url:
    driver.get(ele[0])
    raw_data=driver.find_element_by_class_name("body-wrapper").text
    rows_data=re.split("\d+\.",raw_data)
    rows_data.pop(0)
    rows_data=reduce(lambda x,y:x+y, rows_data)
    rows_data=rows_data.split("\n")
    rows_data=[item for item in rows_data if item != '']
    
    df_temp_invest=pd.DataFrame(np.array(rows_data).reshape(int(len(rows_data)/4),4),columns=col_name2)    
    df_temp_invest["ID"]=ele[1]
    df_investors=df_investors.append(df_temp_invest,ignore_index=True)
    
    

    