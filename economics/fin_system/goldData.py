# -*- coding: utf-8 -*-
"""
Created on Mon Feb 29 22:51:06 2016

贵金属详细数据获取
tushare 通联数据文档
@author: guoxuan
"""

'''
华尔街黄金信息获取黄金
卧槽有错误

'''

from bs4 import BeautifulSoup
import re,os
import urllib
import pandas as pd


url = "http://www.goldtoutiao.com/news/list?status=published&cid=3&order=-created_at&limit=25&page=1"


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language':'zh-CN,zh;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Content-Type':'text/html',
'Connection':'keep-alive',
'Referer':'http://guba.eastmoney.com/list,300418,f_1.html' #注意如果依然不能抓取的话，这里可以设置抓取网站的host
}

opener = urllib.request.build_opener()
#opener.addheaders += [headers]
opener.addheaders=[]
for key, ele in headers.items():
    opener.addheaders+=[(key,ele)] 
data = opener.open(url).read()

indexSoup = BeautifulSoup(data)
statusSoup = BeautifulSoup(indexSoup.prettify().decode("utf-8"))

import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')

'''
通联数据
没有分时数据 也没有黄金延期
'''

mt = ts.Master()
code_info=mt.SecID(assetClass='FU',field='secID,ticker,secShortName,assetClass,exchangeCD,transCurrCD')


st = ts.Market()
AGTD=st.MktFutd(tradeDate='20160229',field='secID,tradeDate,ticker,secShortName,openPrice,closePrice')

F_product=st.MktMFutd(tradeDate='20160229',field='secID,tradeDate,ticker,secShortName,openPrice,closePrice')
