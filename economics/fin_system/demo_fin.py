# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 21:05:58 2016

小飞马金融分析系统
测试
@author: guoxuan

本程序主要展示如何利用tushare包来获取股票数据以及画图


"""
import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.finance as mfinance
from matplotlib.dates import YearLocator, MonthLocator,DayLocator, DateFormatter 
import datatime
# 指数数据
shz=ts.get_hist_data('sh',start='2015-01-01',end='2016-02-26') #一次性获取全部数据
szz=ts.get_hist_data('sz',start='2016-01-01',end='2016-02-26')
cyb=ts.get_hist_data('cyb',start='2016-01-01',end='2016-02-26')




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

## 第二种作图方法
def simple_plot2(dates,data):
    fig=plt.figure(figsize=(10,4))
    plt_sh = fig.add_subplot(1,1,1) 
    plt_sh.plot(dates,data,color='b', linewidth=1.5)
    plt_sh.xaxis.set_major_locator(mdates.DayLocator(bymonthday=range(1,32), interval=30))
    plt_sh.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    for label in plt_sh.xaxis.get_ticklabels():
        label.set_rotation(45)
    plt.setp(plt_sh.get_xticklabels(),visible = True)
    fig.autofmt_xdate()   
    plt.title(u'sh000001')
    plt.show()



## get data from yahoo 
ticker = '600028' # 600028 是"中国石化"的股票代码
ticker += '.ss'   # .ss 表示上证 .sz表示深证

date1 = (2015, 8, 1) # 起始日期，格式：(年，月，日)元组
date2 = (2016, 1, 1)  # 结束日期，格式：(年，月，日)元组

quotes = mfinance.quotes_historical_yahoo_ohlc(ticker, date1, date2)

## 蜡烛图
def plot_K(tuples,name):
    mondays = mdates.WeekdayLocator(mdates.MONDAY)            # 主要刻度
    alldays = mdates.DayLocator()                      # 次要刻度
    #weekFormatter = DateFormatter(‘%b %d‘)     # 如：Jan 12
    mondayFormatter = mdates.DateFormatter('%m-%d-%Y') # 如：2-29-2015
    dayFormatter = mdates.DateFormatter('%d')          # 如：12
    
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    
#    ax.xaxis.set_major_locator(mondays)
#    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=range(1,32), interval=30))
    ax.xaxis.set_minor_locator(mondays)

    ax.xaxis.set_major_formatter(mondayFormatter)
    #ax.xaxis.set_minor_formatter(dayFormatter)
    
    #plot_day_summary(ax, quotes, ticksize=3)
    mfinance.candlestick_ohlc(ax,tuples, width=0.6, colorup='r', colordown='g')
    
    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    
    ax.grid(True)
    plt.title(name)
    plt.show()

def data_candle(DF):
    ## deal with the time date
    ### if the time is string
    df=DF.copy()
    index_name=df.index.name
    col_name=['date_int','open','high','low','close','volume']
        
    df.reset_index(inplace=True)
    dates=df[index_name]
    df['date_int']=convert_plot_date(dates)
       
    tuples = [tuple(x) for x in df[col_name].values]
    
    return tuples
    
def convert_plot_date(dates):
    '''
    the function is aimed at converting string format date into the matplotlib 
    recongizible dates
    function : date2num()
    '''
    dates=pd.to_datetime(dates)
    date_num=mdates.date2num(list(dates))
    
    return date_num
    