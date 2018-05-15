# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 23:09:38 2016

金融分析系统，数据获取 

获取股票相关信息数据并存储
1. 全部股票基本面数据-盈利、营运、成长、偿债、现金 source- tushare 


@author: guoxuan
"""
import matplotlib.pyplot as plt
#%matplotlib inline
import pandas as pd
import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')

path='D:\\Box Sync\\DATAbase\\Finance-Data\\'

basic_stocks=ts.get_stock_basics()

basic_stocks.to_csv(path+'basic_stock.csv',sep=',',header=True,index=True,encoding='utf-8')

years=[2014,2015,2016]
quarters=[1,2,3,4]
for year in years:
    for q in quarters:
        report_t_data=ts.get_report_data(year,q)
        report_t_data=report_t_data.drop_duplicates(subset=['code'], keep='first')

        profit_t_data=ts.get_profit_data(year,q)
        profit_t_data=profit_t_data.drop_duplicates(subset=['code'], keep='first')

        operation_t_data=ts.get_operation_data(year,q)
        operation_t_data=operation_t_data.drop_duplicates(subset=['code'], keep='first')

        growth_t_data=ts.get_growth_data(year,q)
        growth_t_data=growth_t_data.drop_duplicates(subset=['code'], keep='first')

        
        mege_t=report_t_data.merge(profit_t_data,left_on="code",right_on="code",how='left',suffixes=("","_y_del"))          
        drop_cols = [col for col in mege_t.columns if '_y_del' in col]
        mege_t=mege_t.drop_duplicates(subset=['name'], keep=False)
        mege_t.drop(drop_cols,axis=1, inplace=True) 
        
        mege_t=mege_t.merge(operation_t_data,left_on="code",right_on="code",how='left',suffixes=("","_y_del"))          
        drop_cols = [col for col in mege_t.columns if '_y_del' in col]
        mege_t=mege_t.drop_duplicates(subset=['name'], keep=False)
        mege_t.drop(drop_cols,axis=1, inplace=True) 
        
        mege_t=mege_t.merge(growth_t_data,left_on="code",right_on="code",how='left',suffixes=("","_y_del"))          
        drop_cols = [col for col in mege_t.columns if '_y_del' in col]
        mege_t=mege_t.drop_duplicates(subset=['name'], keep=False)
        mege_t.drop(drop_cols,axis=1, inplace=True) 
        
        #output
        mege_t.to_csv(path+'fin_info_'+str(year)+'_'+str(q)+'.csv',sep=',',header=True,index=True,encoding='utf-8')
                
        
        
        
#        #output
#        report_t_data.to_csv(path+'report'+str(year)+'_'+str(q)+'.csv',sep=',',header=True,index=True,encoding='utf-8')
#        profit_t_data.to_csv(path+'profit'+str(year)+'_'+str(q)+'.csv',sep=',',header=True,index=True,encoding='utf-8')
#        operation_t_data.to_csv(path+'operation'+str(year)+'_'+str(q)+'.csv',sep=',',header=True,index=True,encoding='utf-8')
#        growth_t_data.to_csv(path+'growth'+str(year)+'_'+str(q)+'.csv',sep=',',header=True,index=True,encoding='utf-8')
#

# merge part 
years=[2014,2015,2016]
quarters=[1,2,3,4]
for year in years:
    for q in quarters:
        report_t_data=pd.read_csv(path+'report'+str(year)+'_'+str(q)+'.csv',sep=',',header=0,index_col =0,encoding='utf-8')
        report_t_data=report_t_data.drop_duplicates(subset=['code'], keep='first')
        profit_t_data=pd.read_csv(path+'profit'+str(year)+'_'+str(q)+'.csv',sep=',',header=0,index_col =0,encoding='utf-8')
        profit_t_data=profit_t_data.drop_duplicates(subset=['code'], keep='first')
        operation_t_data=pd.read_csv(path+'operation'+str(year)+'_'+str(q)+'.csv',sep=',',header=0,index_col =0,encoding='utf-8')
        operation_t_data=operation_t_data.drop_duplicates(subset=['code'], keep='first')
        growth_t_data=pd.read_csv(path+'growth'+str(year)+'_'+str(q)+'.csv',sep=',',header=0,index_col =0,encoding='utf-8')
        growth_t_data=growth_t_data.drop_duplicates(subset=['code'], keep='first')

        
        mege_t=report_t_data.merge(profit_t_data,left_on="code",right_on="code",how='outer',suffixes=("","_y_del"))          
        drop_cols = [col for col in mege_t.columns if '_y_del' in col]
        mege_t=mege_t.drop_duplicates(subset=['name'], keep='first')
        mege_t.drop(drop_cols,axis=1, inplace=True)
        
        mege_t=mege_t.merge(operation_t_data,left_on="code",right_on="code",how='outer',suffixes=("","_y_del"))          
        drop_cols = [col for col in mege_t.columns if '_y_del' in col]
        mege_t=mege_t.drop_duplicates(subset=['name'], keep=False)
        mege_t.drop(drop_cols,axis=1, inplace=True) 
        
        mege_t=mege_t.merge(growth_t_data,left_on="code",right_on="code",how='outer',suffixes=("","_y_del"))          
        drop_cols = [col for col in mege_t.columns if '_y_del' in col]
        mege_t=mege_t.drop_duplicates(subset=['name'], keep=False)
        mege_t.drop(drop_cols,axis=1, inplace=True) 
        
        mege_t.to_csv(path+'fin_info_'+str(year)+'_'+str(q)+'.csv',sep=',',header=True,index=True,encoding='utf-8')
                
        
'''
股票数据：名称、上市交易所 上市时间， 历史日数据

历史某天的分笔数据


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

'''