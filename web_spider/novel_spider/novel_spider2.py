# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:10:45 2016

@author: xiaofeima

This is aimed at using PhantomJS 
"""


import sys as sys
import codecs
import time, re
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import selenium.common.exceptions as S_exceptions
import copy
import json


'''
initial the page 
'''

#driver = webdriver.Ie("IEDriverserver.exe")
driver = webdriver.Chrome("chromedriver.exe")
#driver = webdriver.Firefox()

url="http://wenshu.court.gov.cn/list/list/?sorttype=1"
file_type="判决书"
year="2007"
show_number=20

condition_url="&conditions=searchWord+"+file_type+"+++文书类型:"+file_type+"&conditions=searchWord+"+year+"+++裁判年份:"+year

def open_page(driver,condition_url,url=url):
    driver.get(url+condition_url)
#    driver.implicitly_wait(2)
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//a[5]")))
    driver.find_element_by_xpath("//div[2]/div[2]/div[2]/div[2]").click()
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//a[5]")))
#    driver.find_element_by_xpath("//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input").click()
#    driver.find_element_by_xpath("//div[5]/div/div[2]/div/div/ul/li").click()  
    flag=input("please select the show number of page (can not automatically choice)")
    if flag:
        return driver
    else:
        exit(1)

def total_number(driver,year,file_type):
    total=driver.find_element_by_xpath("//div[2]/div[4]/span")
    total=total.text
    print("%s 年 共有 %s : %s" %(year,file_type,total))
    print("若每页20条,则需要%s 页" %str(float(total)/20))
    return int(total)
    
label1_pattern="刑事|民事|行政"
label2_pattern="一审|二审|再审|其他"

def get_abstract_info(driver,show_number=show_number):
    abstract_info_dict={
    "label1":"",
    "label2":"",
    "label":"",
    "title":"" ,
    "href":"",
    "court":"",
    "ID":"",
    "date":"",
    "content":"",
    "ID_key":"",
    
    }
    xpath_nav={
    'title_href':"//div[@id='resultList']/div/table/tbody/tr/td/div/a",
    'court_id_date':'//div[@id="resultList"]/div/table/tbody/tr[2]/td/div',
    'abs_content':"//div[@id='resultList']/div/table/tbody/tr[4]/td",

    }
    href_dict={
    "ID_key":"",
    "href":""    
    }    
    
    info_dict_list=[]
    href_dict_list=[]
    ## label of the cases
      
    labels=driver.find_elements_by_css_selector("div.label")
    
    ## title and href of the cases
    title_href=driver.find_elements_by_xpath(xpath_nav['title_href'])
    
    ## institute court and ID and date of the cases
    court_id_date=driver.find_elements_by_xpath(xpath_nav['court_id_date'])
    
    ## absract of the cases
    abs_content=driver.find_elements_by_xpath(xpath_nav["abs_content"])
    
        ########
    try:
        if len(labels)==len(title_href)==len(court_id_date)==len(abs_content):
            current_page= driver.find_elements_by_css_selector("span.current")[1].text           
            n=len(labels)
            for i in range(n):
                content_dict=abstract_info_dict.copy()
                content_dict['label']=labels[i].text
                content_dict['label1']=re.findall(label1_pattern,labels[i].text)[0]
                content_dict['label2']=re.findall(label2_pattern,labels[i].text)[0]
                content_dict['title']=title_href[i].text
                content_dict['href']=title_href[i].get_attribute("href")
                (content_dict['court'],content_dict['ID'],content_dict['date'])=court_id_date[i].text.split()
                content_dict['content']=abs_content[i].text
                content_dict['ID_key']=(int(current_page)-1)*show_number+i
                info_dict_list.append(copy.deepcopy(content_dict))
                
                href_dict['ID_key']=(int(current_page)-1)*show_number+i
                href_dict['href']=title_href[i].get_attribute("href")
                href_dict_list.append(copy.deepcopy(href_dict))
                
    except Exception as e:
        print("page %s has some problem, record it" %current_page)
        print(e)
    
    return info_dict_list,href_dict_list
            
                
def save_link(href_dict_list,path,file_name):
    f=open(path+file_name+".json",'a+')
    f.write(json.dumps(href_dict_list)+"\n")
    f.close()
    print("save the href link")
    
def read_link(path,file_name):
    f=open(path+file_name+".json",'r')
    link_data=[]
    for line in f.readlines():
        ## 加入纠错的标示
        try:
            if type(line)==list:
                link_data+=json.loads(line)
            else:
                link_data.append(json.loads(line))
        
        except:
            print("this chunk is broken")
            



def next_page(driver):
    driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click()
    return driver
    
    
'''
-----------
sqlite3 hacker start
-----------
'''

import sqlite3
path="E:\\"
database_name="abs_info.db"
conn = sqlite3.connect(path+database_name)

c = conn.cursor()

abstract_info_dict={
"label1":"text",
"label2":"text",
"label":"text",
"title":"text" ,
"href":"text",
"court":"text",
"ID":"text",
"date":"text",
"content":"text",
"ID_key":"integer primary key",
}
name_par=[key +" "+ value for key, value in abstract_info_dict.items()]

table_col=",".join(x for x in name_par)

col_name= [key  for key in abstract_info_dict.keys()]

## method to use lists of dictionary insert sqlite3 
# Create table
c.execute('''CREATE TABLE IF NOT EXISTS abs_info
             (%s)''' %table_col)

# 
# Fill the table  data
sql_insert="insert into abs_info (%s) values(:%s)" %(", ".join(x for x in col_name ), ", :".join(x for x in col_name ))

c.executemany(sql_insert, info_list)

# Save (commit) the changes
conn.commit()

for row in c.execute("select %s from abs_info" %", ".join(x for x in col_name )):
    print(row)
## 这一部分提取数据 在我另一个script 中存在的

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

'''
-----------------------------------
get full inforamtion 
----------------------------------
不能用requests 必须要执行完javascript
'''


import requests
from bs4 import BeautifulSoup

headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
'content-type': 'text/html', 
'content-encoding': 'gzip', 
'connection': 'keep-alive',
'Accept-Encoding':'gzip, deflate, sdch'
}

#def get_page_info(url,header=headers):
#    status_flag=0
#    flag=3
#    soup=""
#    try:
#        while flag>=0:
#            html=requests.get(url,headers=header)
#            if html.status_code==200:
#                soup = BeautifulSoup(html.content.decode('utf-8', 'ignore' ),'lxml' )
#                status_flag=1
#    except Exception as e:
#        print("problem with this link ")
#        
#        
#    
#    return soup
#    

nav_dict={
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
    


def get_page_info(url):
    sum_dict={
    "court":"",
    "case_type":"",
    "cause":"",
    "procedure":"",
    "date":"",
    "party":""
    }
    ## open the summary     
    driver.find_element_by_xpath(nav_dict['summary']).click()
    sum_info=driver.find_element_by_xpath("//div[3]/table/tbody")
    ## get the summary info
    for key in sum_dict.keys():   
        sum_dict[key]=sum_info.find_element_by_xpath(nav_dict[key]).text.strip()
    
    law_info=driver.find_element_by_xpath(nav_dict['law_info'])
    sum_dict['law']=law_info.find_element_by_xpath(nav_dict['law']).text.strip()
  

