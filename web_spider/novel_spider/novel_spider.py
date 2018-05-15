# -*- coding: utf-8 -*-
"""
Created on Mon May 23 21:40:49 2016

@author: xiaofeima

webspider for novel 


"""

import requests
from bs4 import BeautifulSoup
import re
from lxml import etree

## prepare for initial link 


header={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36',
'content-type': 'text/html', 
'content-encoding': 'gzip', 
'connection': 'keep-alive',
'Accept-Encoding':'gzip, deflate, sdch'
}

base_url='http://zhuoguji.miaojiangdaoshi.net/'

html=requests.get(base_url,headers=header)
check_flag=[]
check_flag.append("zhuoguji")
## you need to know the charset of the page
## here I know it is utf-8

## use BeautifulSoup to prase the page, 'lxml' is the package
soup = BeautifulSoup(html.content.decode('utf-8', 'ignore' ),'lxml' )

## overview the paresed page 
print(soup.prettify())


## search for the specific link of content 

#soup.select(".quickselect")[0].ul
temp_url=soup.select(".quickselect ul a ")
for i in range(len(temp_url)-1,0,-1):
    if temp_url[i].get("href")!=None :
        if  check_flag[0] in temp_url[i].get("href"):
            cand_url=temp_url[i].get("href")
            break



## get the page 
html=requests.get(cand_url,headers=header)
soup = BeautifulSoup(html.content.decode('utf-8', 'ignore' ),'lxml' )

temp_url=soup.select(".container ul a ")
if  check_flag[0] in temp_url[0].get("href"):
    cand_url=temp_url[0].get("href")

## get the infoed page 
html=requests.get(cand_url,headers=header)
soup = BeautifulSoup(html.content.decode('utf-8', 'ignore' ),'lxml' )


'''
info store
'''

info_novel={
'title':"",
'url':"",
"content":"",
"check_url":'',

}

info_dict=info_novel.copy()

info_dict['title']=soup.select('h2')[0].string.strip()
info_dict['content']=soup.select('.post p')
info_dict['url']=cand_url
info_dict['check_url']=cand_url


## output 
path = "E:\\"
f=open(path+info_dict['title']+".txt",'w')
for line in info_dict['content']:
    try:
        f.write(line.string.strip())
    except:
        pass
f.close()


##-----------------------------------------------------------------------------

base_url='http://zhuoguji.miaojiangdaoshi.net/'

html=requests.get(base_url)
htmlparser = etree.HTMLParser()
tree = etree.parse(html, htmlparser)
xpathselector="//div[4]/div/ul/li[10]/a"
tree.xpath(xpathselector)