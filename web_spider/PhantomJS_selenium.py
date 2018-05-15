# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 15:22:44 2016
PhantomJS and Selenium
pthon 3.5
@author: guoxuan
"""
import time
from selenium import webdriver 
#path = "F:\\github\\Project\\web_spider"
path ="C:\\Users\\guoxuan\\AppData\\Roaming\npm\\node_modules\\phantomjs/lib\\phantom/bin\\"
start_time = time.time()
driver = webdriver.PhantomJS()
driver.set_window_size(1120, 550)
driver.get("https://realpython.com/blog/python/headless-selenium-testing-with-python-and-phantomjs/")
temp=driver.find_element_by_xpath("//h3/following-sibling::p")
#driver.save_screenshot('screen.png') # save a screenshot to disk
print(temp.text)
driver.quit()
elapsed_time = time.time() - start_time
print("total time is: "+ str(elapsed_time) )

# your code
