# -*- coding: utf-8 -*-
"""
Created on Fri May  5 22:58:09 2017

academic citation and fronitor analysis

microsoft academic is a fantastic website! 


-----log-----
shit the website is javascript...
one way to solve is to use  dryscrape  but do not know how to settle it down
another way is to use phantomjs 
http://stackoverflow.com/questions/13287490/is-there-a-way-to-use-phantomjs-in-python
http://stackoverflow.com/questions/8049520/web-scraping-javascript-page-with-python
@author: guoxuan
"""

import requests
import urllib
from bs4 import BeautifulSoup 

Microsoft_Academic="https://academic.microsoft.com/#/search?"
Para_dic={'iq':'',
          'q':'',
          'filters':'',
          'from':"0",
          'sort':"0",
          
          }
# use urllib.parse.urlencode() to join dictionary to url string
          
# query input 
#seach_content=input(prompt='please input the seach content : \n')
seach_content="long term care insurance"
Para_dic['iq']='@'+seach_content+"@"
Para_dic['q']=seach_content

html=requests.get(Microsoft_Academic,params=Para_dic)

soup = BeautifulSoup(html.text, 'html.parser')
print(soup.prettify())
#https://scholar.google.com/scholar?q=long+term+care&btnG=&hl=en&as_sdt=0%2C39

#/search?iq=%40long%20term%20care%20insurance%40&q=long%20term%20care%20insurance&filters=&from=0&sort=0