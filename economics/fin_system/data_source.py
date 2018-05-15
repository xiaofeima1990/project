# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 23:09:38 2016

金融分析系统，数据获取 

## 获取股票相关信息数据

@author: guoxuan
"""
import matplotlib.pyplot as plt
#%matplotlib inline

import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')

'''
股票数据：名称、上市交易所 上市时间， 历史日数据

历史某天的分笔数据
'''
#DataAPI.TickRTIntraDayMoneyFlowOrderGet(securityID=u"000001.XSHE",startTime=u"09:30",endTime=u"11:00",field=u"",pandas="1")
eq_mt = ts.Master()
SecID=eq_mt.SecID(cnSpell='gxgk')

eq_tl=ts.Equity()
candi_stock_ipo=eq_tl.EquIPO(secID='002074.XSHE')



candi_stock_d=ts.get_h_data('002074',start='2006-10-18',end='2016-04-12')

## 获取历史分笔数据

candi_stock_fb = ts.get_tick_data('002074',date='2016-04-12')
candi_stock_fb.head(10)
dates=pd.to_datetime(shz.index)




## 第一种作图方法
def simple_plot(dates,data):
    fig=plt.figure(figsize=(10,4))
    plt_sh = fig.add_subplot(1,1,1) 
    
    daysFmt  = mdates.DateFormatter('%m-%d-%Y')  
    plt_sh.plot(dates,data,color='b', linewidth=1.5)
    plt_sh.xaxis.set_major_formatter(daysFmt)  
    plt_sh.autoscale_view()  
    plt_sh.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    fig.autofmt_xdate() 
    plt.show()



## 新闻热度、市场情绪等指标
fd=ts.Subject()


news_senti=fd.NewsByTickers(ticker='300418',
                            beginDate='20160101',endDate='20160229',
                            field='ticker,secShortName,newsID,newsTitle,relatedScore,sentiment,sentimentScore')
