# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 00:22:23 2016

financial analysis system 

这部分主要从 成交量角度分析 股票市场趋势变动

@author: guoxuan

我坚信：市场的变动取决于多空双方力量的对比，而这是从买卖双方的交易情况来看，成交量是一个关键指标。
它可以反应市场变化的波动性和趋势。
我假设有这么几种形态
1. 上涨时候的成交量变化模式
2. 下跌时候成交量的变化模式
3. 横盘时候的成交量变化模式
4. 关键时刻逆转时候的成交量变化模式
5. 上述个股成交量变动模式中与行业的对比
6. 小盘股和大盘股成交量变动的对比
7. 结合市场情绪和新闻指标来判断人们情绪的影响（难）
8. 重大新闻项目财务数据指标来判断

换手率-> 要看成交量占流通股的比重
股票涨跌涨跌幅度
"""

### 数据获取
# 最高、最低、开盘、收盘、成交量、换手率、
# 资金流量
# ps 简单利用 get hist_data 即可啥都有了 就是近3年的

### 


import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.finance as mfinance
from matplotlib.dates import YearLocator, MonthLocator,DayLocator, DateFormatter 

ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')


## ------------------------------------
# 获取数据
# 利用tushare 接口
# sh=上证指数 sz=深圳成指 hs300=沪深300指数 sz50=上证50 zxb=中小板 cyb=创业板
# 
## ------------------------------------
# 以 牧原股份， 国轩高科， 哈尔斯，宁波港 为例 
candi_stock=ts.get_hist_data('002074',start='2014-01-01',end='2015-12-31') 
sh_index=ts.get_hist_data('sh',start='2014-01-01',end='2015-12-31')
zxb_index=ts.get_hist_data('zxb',start='2014-01-01',end='2015-12-31')

## 获取 交易所日历信息
#mt = ts.Master()
#df_cal = mt.TradeCal(exchangeCD='XSHG', beginDate='20450101', endDate='20151231', field='exchangeCD,calendarDate,isOpen,prevTradeDate')

candi_stock.sort_index(inplace=True)
candi_stock.reset_index(inplace=True)
candi_stock['index']=candi_stock.index
candi_stock=candi_stock.set_index('date')
candi_stock['return']=0
candi_stock.ix[1:,'return']=np.log(candi_stock.ix[1:,'close'].values/candi_stock.ix[0:-1,'close'].values)
candi_stock['flag']=0 ## -1 下跌， 0 震荡 1 上涨
## 对股票进行分解分成 上涨、震荡、下跌三大趋势
## 分3 分5天来简单判断
## i 是循环的日期指示变量
i=5
n=len(candi_stock)
start_point=0
save_period=[]
while i<=n-3:
    i=i+1
    accu_return= candi_stock.ix[start_point:i,'return'].sum()
    # 振荡期
    if candi_stock.ix[i-1,'flag']==0:
        
        if abs(accu_return)>=0.1:
            ## 三天内是否回归
            
            if abs(candi_stock.ix[start_point:i+4,'return'].sum())<0.1:
                continue

            if accu_return<=-0.1:
                retreat=i
                candi_stock.ix[retreat,'flag']=-1
                while retreat >start_point: 
                    if candi_stock.ix[retreat,'return']<-0.03:
                        candi_stock.ix[retreat,'flag']=-1
                        retreat-=1
                    else:
                        
                        start_point=retreat
                        break
            else:
                

                retreat=i
                candi_stock.ix[retreat,'flag']=1
                while retreat >start_point: 
                    if candi_stock.ix[retreat,'return']>0.03:
                        candi_stock.ix[retreat,'flag']=1
                        retreat-=1
                    else:
                        start_point=retreat
                        break
                
    # 上升期 主要以价格判断
    if candi_stock.ix[start_point,'flag']==1:
        if i-start_point<5:
            if candi_stock.ix[start_point:start_point+6,'return'].sum()>0.1:
                candi_stock.ix[start_point:start_point+6,'flag']=1
                i=start_point+4
            else:
                candi_stock.ix[start_point:start_point+5,'flag']=0
        else:
            if (accu_return)>=0.1: # 上涨周期的基本条件
                # 判断什么时候反转 1价差
                if not candi_stock.ix[i:i+4,'return'].sum()>0.03:
                    ## 上涨幅度减缓 
                    ## 判断是否下跌
                
                    if candi_stock.ix[i:i+4,'return'].sum()<-0.05:
                        retreat=i
                        candi_stock.ix[retreat,'flag']=-1
                        while retreat >start_point:
                            if not candi_stock.ix[retreat,'return']>0:
                                candi_stock.ix[retreat,'flag']=-1
                                retreat-=1
                            else:
                                start_point=retreat
                                break
                    else:
                        retreat=i
                        candi_stock.ix[retreat,'flag']=0
                        while retreat >start_point:
                            if not candi_stock.ix[retreat,'return']>0.03:
                                candi_stock.ix[retreat,'flag']=0
                                retreat-=1
                            else:
                                start_point=retreat
                                break
                else:
                    candi_stock.ix[retreat,'flag']=1
                        
## 下跌趋势 主要以价格判断                                
    if candi_stock.ix[start_point,'flag']==-1:
        if i-start_point<5:
            if candi_stock.ix[start_point:start_point+6,'return'].sum()<-0.1:
                candi_stock.ix[start_point:start_point+6,'flag']=-1
                i=start_point+4
            else:
                candi_stock.ix[start_point:start_point+5,'flag']=0
        else:
            if (accu_return)<-0.1: # 上涨周期的基本条件
                # 判断什么时候反转 1价差
                if not candi_stock.ix[i:i+4,'return'].sum()<-0.05:
                    ## 上涨幅度减缓 
                    ## 判断是否下跌
                
                    if candi_stock.ix[i:i+4,'return'].sum()>0.05:
                        retreat=i
                        candi_stock.ix[retreat,'flag']=1
                        while retreat >start_point:
                            if not candi_stock.ix[retreat,'return']<0:
                                candi_stock.ix[retreat,'flag']=1
                                retreat-=1
                            else:
                                start_point=retreat
                                break
                    else:
                        retreat=i
                        candi_stock.ix[retreat,'flag']=0
                        while retreat >start_point:
                            if not candi_stock.ix[retreat,'return']<-0.03:
                                candi_stock.ix[retreat,'flag']=0
                                retreat-=1
                            else:
                                start_point=retreat
                                break
        
                else:
                    candi_stock.ix[retreat,'flag']=-1
            
              
