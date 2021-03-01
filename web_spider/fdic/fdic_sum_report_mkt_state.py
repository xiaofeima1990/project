# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 17:33:27 2021

@author: guoxuan

scriping fdic summary of market share report 
- market share by different location 
- hhi  by different location

 It turns out to calcualte HHI by myself 
 database has some problem
-------------
1. State->County->City->Zip 




"""

import os

current_path=os.path.dirname(os.path.abspath('__file__'))

import sys

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
import time, re
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException,ElementClickInterceptedException 
import selenium.common.exceptions as S_exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pandas as pd





page_load_flag = ".tdHeaderSOD"

COL_mkt_share = ["Date",	"Year",	"state_name",	"Institution_Rank",	"Institution_Name",	"CERT",	
                    "State(Hqtrd)",	"Bank_Class",	"State/Federal_Charter",	"outmkt_num_offices",
                    	"outmkt_Depoits($000)",	"inmkt_num_offices",
                    	"inmkt_Depoits($000)","inmkt_mkt_share"]
COL_HHI = ["Date",	"Year",	"state_name",	"Num_Institutions",	"Total_Assets",	
           "Num_Offices",	"Depoits($000)","HHI"]


def choose_selections(driver, element_id, select_year):
    driver.find_element(By.ID, element_id).click()
    el = driver.find_element(By.ID, element_id) 
    for option in el.find_elements_by_tag_name('option'):
        if select_year in option.text :
            option.click()

def open_page(driver,url):
    # only firefox is OK !!! 
    try:
        driver.set_page_load_timeout(10)
        driver.get(url)
    except TimeoutException as ex:
        check=driver.find_element_by_css_selector(page_load_flag)
        if not check :
            print("problem with the page, restart it")
            driver.quit()
    
    return driver

def initial_driver(driver_path):        
    profile=webdriver.firefox.firefox_profile.FirefoxProfile()
#    # 1 - Allow all images
#    # 2 - Block all images
#    # 3 - Block 3rd party images 
    profile.set_preference("permissions.default.image", 2)
    options = FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options,firefox_profile=profile,executable_path=driver_path)        

    return driver


def open_table(driver,year,sate_index):
    ### 1. open the link 
    driver=open_page(driver,base_url)
    
    
    ### 2. navigate to the market share part 
    pro_forma=driver.find_element_by_id("tdTabDepositMarketShare")
    pro_forma.click()
    
    ### 3. select State option
    msa_selection = driver.find_element_by_css_selector("#divtdTabDepositMarketShare tr:nth-child(1) > td > label")
    msa_selection.click()
    
    ### 4. select year State part
    year_selection = Select(driver.find_element_by_id('MSStateDepositDate'))
    year_selection.select_by_value(year)
    
    state =  driver.find_element_by_id("MSStateRptType1").click()
    
    ### 3. State area get
    state_selection = Select(driver.find_element(By.NAME, "MSStateSelected"))
    state_selection.select_by_index(sate_index)
    state_name = state_selection.all_selected_options[0].text
    time.sleep(0.5)    
    ### 4. generate the report 
    driver.find_element_by_id("SubmitButton").click() 
    time.sleep(5) 
    return driver , state_name


def save_table(driver,Year,Date,state_name):
    ## creat the new empty dataframe
    df_mkt_share = create_dataframe()

    ## navigate to the table 
    table = driver.find_element_by_xpath("//table[3]")
    table_raw_data = table.find_elements_by_tag_name("TR")
    
    if table != '':
        ### table info        
        ## content part market share
        n_row = len(table_raw_data)
        for i in range(7,n_row-2):
            id_i = i-7
            row_data = [Date,Year,state_name,str(id_i)]
            content_list = table_raw_data[i].find_elements_by_tag_name("TD")
            temp_row_data = [ele.text for ele in content_list]
            row_data.extend(temp_row_data)
            df_mkt_share.loc[id_i] = row_data
            id_i = id_i + 1
    
    else:
        df_mkt_share.loc[0] =  [Date,Year,state_name,"0"] + ["-" for x in range(0,10)]

    
    return df_mkt_share


def create_dataframe():
    df_mkt_share = pd.DataFrame(columns= COL_mkt_share)
    return df_mkt_share




if __name__ == '__main__':
    
    
    df_mkt_share = create_dataframe()
    file_path = "D:\\github\\project\\web_spider\\fdic\\"
    file_name1 = "sum_market_share2_state"
    flag = 1
    if flag == 1:
        df_mkt_share.to_csv(file_path+file_name1+'.csv', sep='\t', encoding='utf-8',mode='a',index=False)
        

    '''
    --------------------------------------------------------------------------
    This script works on MSA over years 
    
    '''
    
    ## set up Year 
    Year_list = list(range(2000, 2011))
    Year_list = [str(x) for x in Year_list]
    Date_list = ["06-30-" + x for x in Year_list ]
    
    base_url = "https://www7.fdic.gov/sod/sodMarketBank.asp?barItem=2"
    driver_path="..//geckodriver.exe"
    
    
    driver=initial_driver(driver_path)
    
    ## loop over years and MSAs 
    ### start from year 
    for year_i in range(0,len(Year_list)):
        year = Year_list[year_i]
        Date = Date_list[year_i]
        ### over msa total 392 
        print("working on year "+ year)
        for state_index in range(0,59):            
            
            try:
                ## open the table 
                driver,state_name = open_table(driver,year,state_index)    
                ## save the data
                df_mkt_share_t = save_table(driver,year,Date,state_name)
                
                # save to the dataframe
                df_mkt_share=df_mkt_share.append(df_mkt_share_t,ignore_index=True)
                
            except ElementClickInterceptedException as e:
                print(e)
                driver.find_element_by_id("decline").click()
                ## open the table 
                driver,state_name = open_table(driver,year,state_index)    
                ## save the data
                df_mkt_share_t = save_table(driver,year,Date,state_name)
                # save to the dataframe
                df_mkt_share=df_mkt_share.append(df_mkt_share_t,ignore_index=True)
                
                
            if state_index % 50 == 0:
                time.sleep(5)
        
        df_mkt_share.to_csv(file_path+file_name1+'.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
        df_mkt_share = create_dataframe()