# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 10:56:55 2016

@author: guoxuan
股票等金融信息情绪分析系统
主要数据来源：
股吧  

http://guba.eastmoney.com/list,300418,f_1.html 

"""


from bs4 import BeautifulSoup
import re,os
import urllib
import pandas as pd

code=input("please input the code ")
baseUrl="http://guba.eastmoney.com/list,"+code+",f_"
endUrl=".html"
url = "http://guba.eastmoney.com/list,300418,f_1.html"

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language':'zh-CN,zh;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Content-Type':'text/html; charset=utf-8',
'Connection':'keep-alive',
'Referer':'http://guba.eastmoney.com/list,300418,f_1.html' #注意如果依然不能抓取的话，这里可以设置抓取网站的host
}

#def open_page(i):
#    try:
#        pass
#        
#    
#    except:
#        opener = urllib.request.build_opener()
#        #opener.addheaders += [headers]
#        opener.addheaders=[]
#        for key, ele in headers.items():
#            opener.addheaders+=[(key,ele)] 
#        data = opener.open(url).read().decode('utf-8')
#        
        
opener = urllib.request.build_opener()
#opener.addheaders += [headers]
opener.addheaders=[]
for key, ele in headers.items():
    opener.addheaders+=[(key,ele)] 
data = opener.open(url).read().decode('utf-8')

##################################################
col_name=['date','tag','title','author']
df_info=pd.DataFrame(columns=col_name)
count=0
##################################################

#import urllib.request
#req = urllib.request.Request('http://www.example.com/')
#req.add_header('Referer', 'http://www.python.org/')
#r = urllib.request.urlopen(req)

indexSoup = BeautifulSoup(data)

totalPageHtml = indexSoup.select(".pager")[0]
print(totalPageHtml.text.strip())
totalpage=re.findall('(\d+)',totalPageHtml.text.strip())[0]
num_page=int(float(totalpage)/80)

# num_page 选择需要爬虫的页数

for i in range(1,num_page+1):
    if i>1:    
#        indexSoup=open_page(i)
        try:        
            data = opener.open(baseUrl+str(i)+endUrl).read().decode('utf-8')
            print('new page: '+str(i))
        except Exception as e :
            print(e)
            os.system("pause")
            
                
        indexSoup = BeautifulSoup(data)
    contentHtml=indexSoup.select('#articlelistnew')[0].select(".articleh")
    for ele in contentHtml:
        # 或缺tag名称 话题 新闻 公告 还是股民
        if ele.em is None:
            tag='股友-'
        else:
            tag=ele.em.text
        if tag=='话题':
            continue
        # 获取标题
        title=ele.a.text
        author=ele.select('.l4')[0].text
        date=ele.select('.l6')[0].text
        
        df_info.loc[count]=(date,tag,title,author)
        count+=1


## save the file
filename=code
if not os.path.isfile(filename):
    df_info.to_csv(filename+'-senti.csv',header=True,sep='\t',mode='w',index=False) 
# 加上 总的dataframe 一起
else:
    df_info.to_csv(filename+'-senti.csv',header=True,sep='\t',mode='a',index=False) 



