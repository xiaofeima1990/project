#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 15:06:01 2018

@author: xiaofeima
KMV 计算步骤
- 根据年报得到当时公司资产、权益与负债情况
- 根据KMV公式，计算资产波动率与影子资产价值
- 根据波动率，给定估值期限，得到未来预期波动率水平
- 给定资产增长预期假设，计算未来公司预期资产水平和负债水平
- 根据期权定价公式，得到公司预期权益价值，并得到预期股票价格


"""

import math
import scipy.optimize as scopt
from scipy.stats import norm
import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')
import pandas as pd
import numpy as np
from datetime import datetime 
import sqlite3
from yahoofinancials import YahooFinancials

'''
Obtaining the Data 
1 stock data
2 fundamental data

required data:
    * stock prices (history) 
    * total shares (use markcap and price )
    * total assest
    * short term debt 
    * long  term debt
    * growth rate 
KMV only need
* market cap 
* stock price
* stock volitility 
* interest rate
* long and short term debt 
* time 

'''


    '''
    Chinese data (has problem)
    lack the debt data 
    
    '''
# get the data latest fundamental data 
year=2017
qurater=4
df_basics    = ts.get_stock_basics()
df_report    = ts.get_report_data(year,qurater)
df_profit    = ts.get_profit_data(year,qurater)
df_operation = ts.get_operation_data(year,qurater)
df_growth    = ts.get_growth_data(year,qurater)
df_debt      = ts.get_debtpaying_data(year,qurater)
df_cash      = ts.get_cashflow_data(year,qurater)

# get sqlite database storage
store_path="/Users/xiaofeima/Documents/GitHub/project/economics/fin_system/kmv_sys/"
con = sqlite3.connect(store_path+"stock.sqlite")
df_basics.to_sql("basics", con, if_exists="replace")
df_report.to_sql("report", con, if_exists="replace")
df_profit.to_sql("profit", con, if_exists="replace")
df_operation.to_sql("operation", con, if_exists="replace")
df_growth.to_sql("growth", con, if_exists="replace")
df_debt.to_sql("debt", con, if_exists="replace")
df_cash.to_sql("cash", con, if_exists="replace")
con.close()


# select the key parameters
# basic totals totalAssets


candi_stock=['000002','600999','000024','000958']
index_candi_stock=[int(x) for x in candi_stock]
ts.get_hist_data('000002',start='2018-01-01',end='2018-04-01')

'''
US stock 

market cap
stock price
long term short term debt 
interest rate 


'''
ticker = 'AAPL'
yahoo_financials = YahooFinancials(ticker)

stock_info={
        'marketCap': 0 ,
        'price_c':0,
        'i_rate':0,
        'long_debt':0,
        'short_debt':0,
        'ROE':0,
        'num_shares':0,
        }


stock_summary = yahoo_financials.get_stock_summary_data()

stock_info['num_shares']=stock_summary[ticker]['marketCap']/stock_summary[ticker]['previousClose']
stock_info['price_c']=172.23
stock_info['marketCap']=stock_info['price_c']*stock_info['num_shares']



balance_sheet_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'balance')
income_statement_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'income')
all_statement_data_qt =  yahoo_financials.get_financial_stmts('quarterly', ['income', 'cash', 'balance'])
earnings_data = yahoo_financials.get_stock_earnings_data()
net_income = yahoo_financials.get_net_income()
historical_stock_prices = yahoo_financials.get_historical_stock_data('2018-01-01', '2018-04-20', 'daily')
