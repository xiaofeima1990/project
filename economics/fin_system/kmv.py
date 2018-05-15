# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 17:56:10 2017

@author: guoxuan

KMV calculation

"""
import math
import scipy.optimize as scopt
from scipy.stats import norm
import tushare as ts

'''
股权价值波动率sigma_e 计算
'''

St=ts.get_k_data('000002', index=False,autype='qfq',ktype='D',start='2014-01-01',end='2017-06-09')


def daily_return(prices):
    return math.log(prices[:-1] / prices[1:])
    
mu_e=daily_return(St)

sigma=math.sqrt(St.var()*250)


E=6325611827.0       #股权价值
sigma_e=0.522401135 #年化股票收益波动率
r=0.0325           #无风险利率
T=1              #时间
DPT=2646251848.0     #违约点 短期负债+长期负债*0.5


def f(X):
    V=X[0]
    sigma_a=X[1]
    d1=(math.log(V/DPT)+(r+0.5*sigma_a**2)**T)/(sigma_a*math.sqrt(T))
    d2=d1-sigma_a*math.sqrt(T)
    
    return [ (E-V*norm.cdf(d1)+DPT*math.exp(-r*T)*norm.cdf(d2) )**2 ,
 (sigma_e-norm.cdf(d1)*V*sigma_a/E )**2 ]

KMV_result = scopt.fsolve(f, [8885510950.0, 0.141])
 
 
def ff(X):
    V=float(X[0])
    sigma_a=float(X[1])
    d1=(math.log(V/DPT)+(r+0.5*sigma_a**2)*T)/(sigma_a*math.sqrt(T))
    d2=d1-sigma_a*math.sqrt(T)
    
    return (E-V*norm.cdf(d1)+DPT*math.exp(-r*T)*norm.cdf(d2) )**2 + (sigma_e-norm.cdf(d1)*V*sigma_a/E )**2 

 
    
KMV_result = scopt.fmin(ff, [8885510950.3 , 0.37])
    