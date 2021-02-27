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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
import selenium.common.exceptions as S_exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pandas as pd




page_load_flag = ".tdHeaderSOD"




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


if __name__ == '__main__':
    
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