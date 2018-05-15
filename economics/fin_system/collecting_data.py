# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 00:04:21 2017

@author: guoxuan

collecting testing data used for asset pricing test

stock data
fundamental data 

"""


import matplotlib.pyplot as plt
#%matplotlib inline
import pandas as pd
import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')

path='D:\\Box Sync\\DATAbase\\Finance-Data\\'



# get stock basic information 
eq = ts.Equity()
stock_basic = eq.Equ(equTypeCD='A', listStatusCD='L',field='secID,ticker,secShortName,totalShares,nonrestFloatShares,TShEquity')

stock_small_list=stock_basic.loc[stock_basic['secID'].str.contains('002'),]
stock_small_list.to_csv(path+"5_15-17.csv",header=True,encoding='utf-8',sep='\t')

# get stock industy 
eq = ts.Equity()
stock_industry = eq.EquIndustry(industryVersionCD='010301')



mk=ts.Market()
stock_all_history=mk.MktEqud(secID=','.join(stock_small_list['secID'].values[:5]),beginDate='20150101',endDate='20170905')

stock_all_history.to_csv(path+"5_15-17.csv",header=True,encoding='utf-8',sep='\t')


# financial report info  要分银行 证券 和一般工商业
bd = ts.Fundamental()
df_BSIndu_temp = bd.FdmtBSIndu(ticker='000002', field='reportType,secID,ticker,endDate,cashCEquiv,tradingFA,NotesReceiv,AR,prepayment,inventories,TCA,LTReceive,LTEquityInvest,investRealEstate,fixedAssets,RD,TNCA,TAssets,STBorr,tradingFL,NotesPayable,AP,advanceReceipts,TCL,LTBorr,TNCL,TLiab,paidInCapital,retainedEarnings,TShEquity')
df_BSIndu_clean = df_BSIndu_temp.drop_duplicates(subset=['ticker','endDate'],keep='first')


bd = ts.Fundamental()
df_ISIndu_temp = bd.FdmtISIndu(ticker='000002', field='reportType,secID,ticker,endDate,tRevenue,revenue,TCogs,COGS,operateProfit,NoperateIncome,TProfit,intExp,incomeTax,NIncome,basicEPS')
df_ISIndu_clean = df_ISIndu_temp.drop_duplicates(subset=['ticker','reportType','endDate'],keep='first')

bd = ts.Fundamental()
df_CFIndu_temp = bd.FdmtCFIndu(ticker='000002', field='reportType,secID,ticker,endDate,CFrSaleGS,CInfFrOperateA,CPaidGS,COutfOperateA,NCFOperateA,gainInvest,CInfFrInvestA,purFixAssetsOth,COutfFrInvestA,NCFFrInvestA,CFrBorr,CFrIssueBond,CInfFrFinanA,CPaidForDebts,CPaidDivProfInt,COutfFrFinanA,NCFFrFinanA,NCEEndBal')
df_CFIndu_clean = df_CFIndu_temp.drop_duplicates(subset=['ticker','reportType','endDate'],keep='first')

