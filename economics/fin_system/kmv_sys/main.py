# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 23:32:20 2017
KMV-stock price evaluation 
@author: guoxuan

This project is intended to uniform my past work for the stock evulation.
The method is based on KMV or more essentially the BS option pricing formula

The model idea is described as follows:
    1 From KMV , we use the stock price (equity value) and volitality plus debt 
      data to evaluate the firms total asset market value first. And based on firm's 
      total asset market value and asset growth rate , we get the current period 
      expected total asset market value. Then we use so called DPT= short term 
      debt +0.5*long term debt to calculate defalut distance DD=(EA-DPT)/sigma_A 
      
    2 This procedure motivate me to think in another way, which use the fiscal 
      report asset value, debt value and stock market data to construct a new 
      way to evaluate the future/current stock price. There have 3 main steps:
          1 use stock market data to get equity value and volatility, and plus 
            the asset value and debt value, to calculate the "risk exposure"
          2 use reported data till current date stock price data to calucate 
            new/current volatility of equity. Use this volatility to calucate 
            the risk exposure volatility (similar formula). 
          3 Calculate the "confidence interval" for the future/current risk exposure
          4 use ROA, total asset value( get expected total asset), asset volatility,
            future/current exposure to calculate expected equity value by BS-formula
            and we can get the interval estimation of expected equity value.

            
            
The project consist of three main part:
    1 get the data
    2 calcuation
    3 further analysis
"""
import math
import scipy.optimize as scopt
from scipy.stats import norm
import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')
import pandas as pd
import numpy as np
from datetime import datetime 


'''
Obtaining the Data 
1 stock data
2 fundamental data
'''

candi_stock=['000002','600999','000024','000958']
index_candi_stock=[int(x) for x in candi_stock]
stock_info_col=['pre_mean','pre_std','cur_mean','cur_std','eqMktValue_pre','eqMktValue_cur']
stock_FD_col=['TAssets','TLiab']
stock_IS_col=['tRevenue','operateProfit','NIncome']
stock_FI_col=['ROA1','ROA2','ROA']
stock_info=pd.DataFrame(index=index_candi_stock,columns=[stock_info_col+stock_FD_col+stock_IS_col+stock_FI_col])
Time_pick='2011-09-30'
Time_pick2='2011-11-30'

# get the stock row data 
market=ts.Market()
stock_pre=market.MktEqud(ticker=','.join(candi_stock),beginDate='20110101',endDate='20110930',field='ticker,secShortName,tradeDate,preClosePrice,ClosePrice,marketValue,chgPct,,PB')
stock_cur=market.MktEqud(ticker=','.join(candi_stock),beginDate='20111001',endDate='20111130',field='ticker,secShortName,tradeDate,preClosePrice,ClosePrice,marketValue,chgPct,,PB')
g_stock_pre=stock_pre.groupby('ticker')
g_stock_cur=stock_cur.groupby('ticker')

for name in index_candi_stock:
    temp_pre=g_stock_pre.get_group(name)
    temp_cur=g_stock_cur.get_group(name)
    stock_info.loc[name,stock_info_col]=[temp_pre['chgPct'].mean(), temp_pre['chgPct'].var()**0.5,temp_cur['chgPct'].mean(), temp_cur['chgPct'].var()**0.5, 
                   temp_pre.loc[stock_pre['tradeDate']==Time_pick,'marketValue'].values[0],
                   temp_cur.loc[stock_cur['tradeDate']==Time_pick2,'marketValue'].values[0]]
              
            
#stock=ts.get_k_data(code=candi_stock[1],start='2011-01-01',end='2011-12-31',ktype='D')
#ticker,secShortName,tradeDate,openPrice,closePrice,negMarketValue,marketValue,isOpen


#
#eq = ts.Equity()
#df = eq.Equ(ticker=','.join(candi_stock),equTypeCD='A', listStatusCD='L', field='ticker,secShortName,totalShares,nonrestFloatShares')
#df['ticker'] = df['ticker'].map(lambda x: str(x).zfill(6))


# get the stock fundamental data  plus ROA ROE netincome ~

fd = ts.Fundamental()
df_BS_temp=fd.FdmtBS(ticker=','.join(candi_stock),beginDate='20110101',endDate='20111231', field='reportType,secID,ticker,endDate,fiscalPeriod,TAssets,TCA,TLiab,TCL')
df_BS_clean = df_BS_temp.drop_duplicates(subset=['ticker','reportType','endDate'],keep='first')
g_df_BS_clean=df_BS_clean.groupby(['ticker','reportType'])
df_IS_temp=fd.FdmtIS(ticker=','.join(candi_stock),beginDate='20110101',endDate='20111231', field='reportType,secID,ticker,endDate,fiscalPeriod,tRevenue,operateProfit,NIncome')
df_IS_clean = df_IS_temp.drop_duplicates(subset=['ticker','endDate','reportType'],keep='first')
g_df_IS_clean=df_IS_clean.groupby(['ticker','reportType'])

for name in index_candi_stock:
    temp=g_df_BS_clean.get_group((name,'Q3'))
    stock_info.loc[name,stock_FD_col]=temp[stock_FD_col].values
    temp2=g_df_IS_clean.get_group((name,'CQ3'))
    stock_info.loc[name,stock_IS_col]=temp2[stock_IS_col].values
    stock_info.loc[name,stock_FI_col]=temp2[stock_IS_col].values/temp[stock_FD_col[0]].values


    
    
'''
Calculate the risk exposure
A, E, D is very big, so it is not very suitable to do the optimization, we can divide both 
side by E to normalize such question
'''




name=2
T=0.25
r=0.03
(equityValue,equityStd,TAssets,ROA)=stock_info.loc[name,['eqMktValue_cur','pre_std','TAssets','ROA']]
para=(equityValue,equityStd,TAssets*(1+ROA/9),T,r)


def BS_1(X,equityValue,equityStd,TAssets,T,r):
    D=X[0]
    sigma_a=X[1]
    sigma_e=equityStd
    A=TAssets/equityValue
    d1=(math.log(A/D)+(r+0.5*sigma_a**2)**T)/(sigma_a*math.sqrt(T))
    d2=d1-sigma_a*math.sqrt(T)
    
    return [ (1-A*norm.cdf(d1)+D*math.exp(-r*T)*norm.cdf(d2) )**2 ,
 (sigma_e-norm.cdf(d1)*A*sigma_a )**2 ]
    
KMV_result = scopt.fsolve(BS_1, [1, 0.441],args=para)
 
    
def BS_2(X,equityValue,equityStd,TAssets,T,r):
    D=X[0]
    sigma_a=X[1]
    
    sigma_e=equityStd
    A=TAssets/equityValue

    d1=(math.log(A/D)+(r+0.5*sigma_a**2)*T)/(sigma_a*math.sqrt(T))
    d2=d1-sigma_a*math.sqrt(T)
    
    return  (1-A*norm.cdf(d1)+D*math.exp(-r*T)*norm.cdf(d2) )**2 + (sigma_e-norm.cdf(d1)*A*sigma_a )**2 
    
    
KMV_result2 = scopt.fmin_tnc(BS_2,[2,0.2],bounds=[[10**-8,4],[10**-8,1]],args=para,approx_grad=True)


# the risk exposure is 
DD=KMV_result2[0][0]
sigma_a=KMV_result2[0][1]


'''
the confidence interval for risk exposure in current period
1 calculate the volatility using current data (maybe plus the on year on year base data)
2 calculate VaR from now on to the future date you expected
3 calculate the interval
'''

def volatility_risk(X,sigma_e1,DD,r,t):
    d2=(math.log(DD)+(r-0.5*X**2)**t)/(X*math.sqrt(t))
    return (sigma_e1-DD*norm.cdf(d2)*X)**2

cur_std=stock_info.loc[name,'cur_std']
sigma_d = scopt.fsolve(volatility_risk, cur_std, args=(cur_std,DD,r,1/6))[0]


VaR=1.*sigma_d*30**0.5


'''
calculate the expected equity value by BS formula
1 use current date to replace the DD exposure 
2 use ROA data to update TAssets 
3 calculate expected equity value
'''

abs_DD=DD*stock_info.loc[name,'eqMktValue_cur']
ROA=stock_info.loc[name,'ROA']

def BS_final(A,abs_DD,sigma_a,r,T):
    
    d1=(math.log(A/abs_DD)+(r+0.5*sigma_a**2)**T)/(sigma_a*math.sqrt(T))
    d2=d1-sigma_a*math.sqrt(T)
    
    return A*norm.cdf(d1)-abs_DD*math.exp(-r*T)*norm.cdf(d2) 

Ex_eqMktValue=BS_final(TAssets*(1+ROA/3),abs_DD*(1+VaR),sigma_a,r,2/12)




