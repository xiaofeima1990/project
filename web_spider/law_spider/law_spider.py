# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:10:45 2016

@author: xiaofeima

This is aimed at spider law files and doing some analysis for this 

1. question
卧槽网站防爬虫机制太蛋疼了
超过几百页就tmd给我reset

解决办法：
1. 分类分细一些
2. 成功发现可以进行分period 分月或者更细的爬去信息

"""


import sys as sys
import codecs
import time, re,math,urllib
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,UnexpectedAlertPresentException
import selenium.common.exceptions as S_exceptions

import copy
import json


'''
initial the page 
'''
####---------------------------------
#    全局变量 
####---------------------------------
URL="http://wenshu.court.gov.cn/list/list/?sorttype=1"
FILE_TYPE="判决书"
YEAR="2007"
show_number=20
CAN_XPATH="//div[5]/div/div[2]/div/div/ul/li[4]"
RERESH='document.evaluate("%s",document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()' %CAN_XPATH


class law_spider_link():
    label1_pattern="刑事|民事|行政"
    label2_pattern="一审|二审|再审|其他"
    xpath_nav={
        'title_href':"//div[@id='resultList']/div/table/tbody/tr/td/div/a",
        'court_id_date':'//div[@id="resultList"]/div/table/tbody/tr[2]/td/div',
        'abs_content':"//div[@id='resultList']/div/table/tbody/tr[4]/td",
    
        }

    
    def __init__(self,url=URL,show_number=20):
        '''
        search_dict={ file_type : key_word}
        '''
        self.url=url
#        self.year=year
        self.show_number=show_number
        f=input("please choose which web browser 1 = firefox 2=chrome 3= IE")
        if int(f)==1:
            self.driver = webdriver.Firefox()
        elif int(f)==2:
            self.driver= webdriver.Chrome("chromedriver.exe")
        else:
            self.driver = webdriver.Ie("IEDriverserver.exe")
#        self.condition_url2="&conditions=searchWord+"+self.file_type+"+++文书类型:"+self.file_type+"&conditions=searchWord+"+self.year+"+++裁判年份:"+self.year
#        self.condition_url=""        
#        for  file_type , key_word in search_dict.items():        
#            self.condition_url+="&conditions=searchWord+%s+++%s:%s" %(key_word,file_type,key_word)
        self.page_flag=0
#        self.unquote=urllib.parse.unquote(self.url+self.condition_url)        
        print("init the selenium driver")

    def set_search_url(self,search_dict,year):
        '''
        search_dict contains basic information for search, 
        '''
        self.condition_url=""        
        for  file_type , key_word in search_dict.items():        
            self.condition_url+="&conditions=searchWord+%s+++%s:%s" %(key_word,file_type,key_word)
        self.year=year
#        self.url_t=urllib.parse.quote(self.url+self.condition_url,safe="%:/?+&=",encoding='utf-8')        
        
        
    def split_time_search(self,search_dict,start_date,end_date):
        self.condition_url=""
        for  file_type , key_word in search_dict.items():        
            self.condition_url+="&conditions=searchWord+%s+++%s:%s" %(key_word,file_type,key_word)
        self.condition_url+="&conditions=searchWord++CPRQ++%s:%s TO %s" %("裁判日期",start_date,end_date)
                
    def set_CAN_XPATH(self, XPATH):
        self.can_xpath=XPATH
    def set_javacript_xpath(self):
        self.js_xpath='document.evaluate("%s",document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()' %self.can_xpath
    def execute_script(self,xpath=CAN_XPATH):
        refresh='document.evaluate("%s",document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()' %xpath
        self.driver.execute_script(refresh)

    def open_page(self,url="",flag=1):
        self.url_t=urllib.parse.quote(self.url+self.condition_url,safe="%:/?+&=",encoding='utf-8')
        if flag==1:
            self.driver.get(self.url_t)
        else:
            self.driver.get(url)
        i=3
        while i>0 :
            try:
                self.driver.implicitly_wait(3)
        
    #    driver.implicitly_wait(2)
        
                WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//div[2]/div[2]/div[2]/div[2]")))
        
        # 升序按日期排序        
                self.driver.find_element_by_xpath("//div[2]/div[2]/div[2]/div[2]").click()  
                WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input")))
    #    driver.find_element_by_xpath("//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input").click()
    #    driver.find_element_by_xpath("//div[5]/div/div[2]/div/div/ul/li").click()  
                time.sleep(3)        
#        self.driver.find_element_by_xpath("//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input").click()
#        WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[5]/div/div[2]/div/div/ul/li[4]")))
#        self.driver.find_element_by_xpath("//div[5]/div/div[2]/div/div/ul/li[4]").click()
                self.execute_script()
                break
            except Exception as e:
                self.driver.refresh()
                i=i-1
                if i==0:
                    print('open page failed ')
                    print(e)
                
                
        try:
            WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[2]/div[2]/div[2]/div[2]")))
            
            print("please make sure that the page show correctly")
            time.sleep(10)
        except:
            print("page load failed")
            print("something wrong with the program")
            exit(1)
            
        
        
        


    def total_number(self):
        i=3
        while i>=0:
            
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.ID,"span_datacount")))
#            total=self.driver.find_element_by_xpath("//div[2]/div[4]/span")
            total=self.driver.find_element_by_id("span_datacount")
            
            total=total.text
            try :
                xx=float(total)
                break
            except:
                i=i-1
                
            
        print("%s 年 共有 %s" %(self.year,total))
        print("若每页20条,则需要%s 页" %str(int(total)/20.0))
        if int(total)<=20:
            result=1
        else:
            result=math.ceil(float(total)/20)
        return result
    


    def get_abstract_info(self):
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

        href_dict={
        "ID_key":"",
        "href":""    
        }    
        
        info_dict_list=[]
        href_dict_list=[]
        
        f=0
        ## check if page is loaded correctly
        while f==0 :        
            try:            
                WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"span.current")))
                f=1
            except Exception as e:
                if "VisitRemind.html" in self.driver.current_url:
                    input("crack need to input verfication code to process")
                    
                self.next_page()
        
        ## label of the cases
#        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//a[5]")))  
        labels=self.driver.find_elements_by_css_selector("div.label")
        
        ## title and href of the cases
        title_href=self.driver.find_elements_by_xpath(self.xpath_nav['title_href'])
        
        ## institute court and ID and date of the cases
        court_id_date=self.driver.find_elements_by_xpath(self.xpath_nav['court_id_date'])
        
        ## absract of the cases
        abs_content=self.driver.find_elements_by_xpath(self.xpath_nav["abs_content"])
        
            ########
        try:
            if len(labels)==len(title_href)==len(court_id_date)==len(abs_content):
                              
                current_page= self.driver.find_elements_by_css_selector("span.current")[-1].text           
                print("current page is " + current_page)                
                n=len(labels)
                for i in range(n):
                    content_dict=abstract_info_dict.copy()
                    content_dict['label']=labels[i].text
                    content_dict['label1']=re.findall(self.label1_pattern,labels[i].text)[0]
                    content_dict['label2']=re.findall(self.label2_pattern,labels[i].text)[0]
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
            error_dict={
            "ful_url":  self.url+self.condition_url,
            "problem_page":current_page
            
            }
            f_error=open('error_link.json','a')
            f_error.write(json.dumps(error_dict)+"\n")
            f_error.close()
            
        
        return info_dict_list,href_dict_list

    def next_page(self):
        current_page= self.driver.find_elements_by_css_selector("span.current")[-1].text
        if int(current_page)<25:
            try:
                self.driver.find_element_by_xpath("//div[2]/div[2]/div[2]/div[2]").click()
    #            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//a[contains(text(),'下一页')]")))
                 ## this part is dealing with the case which the page is larger than 25
                self.driver.implicitly_wait(5)
            except Exception as e:
                
                print(e)
                input("wait for problem sovling , press any key to continue ")

            
                    
        else:
            try:
                self.driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click()
                time.sleep(5)
            except Exception as e:
                
                print(e)
                input("wait for problem sovling , press any key to continue ")              
            try:
                if self.driver.switch_to_alert():
                    self.driver.switch_to_alert().accept()
                self.driver.execute_script(RERESH)
                self.driver.implicitly_wait(5)
            except:
                print("no alert")
                
            
#            self.driver.switch_to_alert().accept()
#            time.sleep(5)
#            WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input")))
            
#            self.driver.find_element_by_xpath("//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input").click()
#            WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[5]/div/div[2]/div/div/ul/li[4]")))
#            self.driver.find_element_by_xpath("//div[5]/div/div[2]/div/div/ul/li[4]").click()
# 
        try:
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"span.current")))
            current_page= self.driver.find_elements_by_css_selector("span.current")[-1].text
            print("start next page %s " %current_page)
        except Exception as e:
            print(e)
            print("next page may be end")
#    def __del__(self):
#        self.driver.close()
        
def save_link(href_dict_list,path,file_name):
    f=open(path+file_name+".json",'a')
    f.write(json.dumps(href_dict_list)+"\n")
    f.close()
    print("save the href link")
    
def read_link(path,file_name):
    f=open(path+file_name+".json",'r')
    link_data=[]
    for line in f.readlines():
        ## 加入纠错的标示
        temp=json.loads(line)
        link_data+=temp
#        try:
#            if type(line)==list:
#                link_data+=[x for x in json.loads(line)]
#            else:
#                link_data+=json.loads(line)
#        
#        except:
#            print("this chunk is broken")
    
    
    return link_data
                
    


 
'''
-----------------------------------
get full inforamtion 
----------------------------------
'''

class law_spider_info():
    

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
    
    def __init__(self):
#        self.driver= webdriver.Chrome("chromedriver.exe") 
        self.driver= webdriver.Firefox() 
#        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//div[@id='DivContent']")))

    def get_page_abs_info(self,link_data):
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
        self.driver.get(link_data['href'])        
        
        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//div[@id='DivContent']")))
        self.driver.implicitly_wait(3)
        ## open the summary     
        self.driver.find_element_by_xpath(self.nav_abs_dict['summary']).click()
        sum_info=self.driver.find_element_by_xpath(self.summary_nav)
        ## get the summary info
        for key in sum_dict.keys():
            try: 
                sum_dict[key]=sum_info.find_element_by_xpath(self.nav_abs_dict[key]).text.strip()
            except:
                sum_dict[key]=""
                
        law_info=self.driver.find_element_by_xpath(self.nav_abs_dict['law_info'])
        sum_dict['law']=law_info.find_element_by_xpath(self.nav_abs_dict['law']).text.strip()
      
    
        
    
        sum_dict2={
        "title":"",
        "date2":"",
        "full_content":""        
        }
        for key in sum_dict2.keys():        
            sum_dict2[key]=self.driver.find_element_by_xpath(self.nav_dict[key]).text.strip()
        
        sum_dict2['date2']=re.findall("发布日期：(.+)",sum_dict['date'])[0]
        
        sum_dict.update(sum_dict2)
        
        return sum_dict
       
'''
database operation 
'''       

#import spider_database
#        
#class law_spider_data(spider_database):
#    def __init__(self, path="",database_name):
#        super(law_spider_data,self).__init__()
#    
#    
    

#name_par=[key +" "+ value for key, value in abstract_info_dict.items()]
#
#table_col=",".join(x for x in name_par)
#
#col_name= [key  for key in abstract_info_dict.keys()]
#
#


'''
javascript 
'''
## 进行 xpath 选取
#var x = document.evaluate("//div[5]/div/div[2]/div/div/ul/li[4]",document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue

## 进行 class name 选取
#document.getElementsByClassName('selBtn')[6].click()
#
#def next_page(driver):
#    current_page= driver.find_elements_by_css_selector("span.current")[-1].text
#    
#    try:
#        driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click()
##            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//a[contains(text(),'下一页')]")))
#         ## this part is dealing with the case which the page is larger than 25
#        driver.implicitly_wait(3)
#    except Exception as e:
#        print("warning")
#        print(e)
##            print(e)
##            input("wait for problem sovling , press any key to continue ")
#
#        
#    if int(current_page)>25:
#        
#        print("larger than 25")
#        driver.switch_to_alert().accept()
#        time.sleep(5)
#        WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[5]/div/div[2]/div/table/tbody/tr/td[2]/input")))
#        
#        
        
#            driver.find_element_by_xpath("//div[5]/div/div[2]/div/div/ul/li[4]").click()
 
    
#    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.XPATH,"//a[contains(text(),'下一页')]")))
#    current_page= driver.find_elements_by_css_selector("span.current")[-1].text
#    print("start next page %s " %current_page)

def next_page2(driver):
    driver.find_element_by_xpath("//a[contains(text(),'下一页')]").click()
    time.sleep(3)
    try:
        if driver.switch_to_alert():
            driver.switch_to_alert().accept()
        driver.execute_script(RERESH)
    except:
        print("no alert")