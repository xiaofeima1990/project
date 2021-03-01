# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 17:33:27 2021

@author: guoxuan

scriping fdic summary of market share report 
- market share by different location 
- hhi  by different location

-------------
1. State->County->City->Zip 
2. Metropolitan Statistical Area (MSA)


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
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
import selenium.common.exceptions as S_exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pandas as pd




page_load_flag = ".tdHeaderSOD"

COL_mkt_share = ["Date",	"Year",	"MSA_name",	"Institution_Rank"	"Institution_Name",	"CERT",	
                    "State(Hqtrd)",	"Bank_Class",	"State/Federal_Charter",	"Total_Assets",
                    "Offices",	"Depoits($000)",	"Market_Share",	"Squared_Market_Share"]
COL_HHI = ["Date",	"Year",	"MSA_name",	"Num_Institutions",	"Total_Assets",	
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
        driver.set_page_load_timeout(5)
        driver.get(url)
    except TimeoutException as ex:
        check=driver.find_element_by_css_selector(page_load_flag)
        if not check :
            print("problem with the page, restart it")
            driver.quit()
    
    return driver

def open_table(driver,year,msa_location)




def create_dataframe():
    df_mkt_share = pd.DataFrame(columns= COL_mkt_share)
    df_HHI = pd.DataFrame(columns= COL_HHI)
    return (df_mkt_share, df_HHI)




if __name__ == '__main__':
    
    
    (df_mkt_share, df_HHI) = create_dataframe()
    Year = "2015"
    Date = "06-30-"+Year
    
    base_url = "https://www7.fdic.gov/sod/sodMarketBank.asp?barItem=2"
    driver_path="..//geckodriver.exe"
        
        
    profile=webdriver.firefox.firefox_profile.FirefoxProfile()
#    # 1 - Allow all images
#    # 2 - Block all images
#    # 3 - Block 3rd party images 
    profile.set_preference("permissions.default.image", 2)

    options = FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options,firefox_profile=profile,executable_path=driver_path)        
        
    driver=open_page(driver,base_url)
    
    
    
    ### navigate to the HHI part 
    pro_forma=driver.find_element_by_xpath("//font[contains(.,'Pro-Forma')]")
    pro_forma.click()
    
    '''
    Report Creation:
        1.GEO area
        
    '''
    ### 1. geo area
    geo_selection = driver.find_element_by_css_selector("#divtdTabProForma tr:nth-child(2) > td > label")
    geo_selection.click()
    ### 2. select year MSA part 
    year_selection = Select(driver.find_element_by_id('PFMSADepositDate'))
    year_selection.select_by_value(Year)
    
    ### 3. msa area
    msa_selection = Select(driver.find_element(By.NAME, "PFMSASelected"))
    msa_selection.deselect_all()
    msa_selection.select_by_index(4)
    
    
    ### 4. generate the report 
    driver.find_element_by_id("SubmitButton").click() 
    
    
    '''
    Table part
    
    '''
    
    ## check the total assets part 
    asset_selection = Select(driver.find_element_by_name('sAssetsAsOf'))
    asset_selection.select_by_value("June 30, "+Year)
    
    
    table = driver.find_element_by_css_selector('.table')
    
    table_raw_data = table.find_elements_by_tag_name("TR")
    
    ### table info
    table_msa_info = table_raw_data[3].text
    ## header part  not important 
    # header_list = table_raw_data[4].find_elements_by_tag_name("TH")
    row_data_common = [Date,Year,table_msa_info]
    ## content part market share
    n_row = len(table_raw_data)
    for i in range(5,n_row-2):
        id_i = i-5
        row_data = [Date,Year,table_msa_info]
        content_list = table_raw_data[i].find_elements_by_tag_name("TD")
        temp_row_data = [ele.text for ele in content_list]
        temp_row_data = temp_row_data[2:]
        row_data.extend(temp_row_data)
        df_mkt_share.loc[id_i] = row_data
        id_i = id_i + 1
        
        
    idx_i = 0 
    content_list = table_raw_data[-2].find_elements_by_tag_name("TD")
    temp_row_data = [ele.text for ele in content_list]
    Num_Institutions = re.findall("\d+",temp_row_data[0])
    temp_row_data.pop(-2)
    temp_row_data.pop(0)
    row_data = [Date,Year,table_msa_info] + Num_Institutions+ temp_row_data
    df_HHI.loc[idx_i] = row_data
    idx_i = 1
    
    