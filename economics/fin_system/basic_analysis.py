# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 16:31:03 2017

@author: guoxuan

股票基本面分析
"""

import matplotlib.pyplot as plt
#%matplotlib inline

import tushare as ts
ts.set_token('6cbc132dcf304322dc7b6f1d714d792fe224049b2038abf29e7711bf71334b52')

import pandas as pd
path='D:\\Box Sync\\DATAbase\\Finance-Data\\'

# 数据获取
# 获取上证 深证 沪深300 
hs300=ts.get_k_data('399300', index=True,ktype='D',start='2014-01-01',end='2017-06-09')
shz=ts.get_k_data('000001', index=True,ktype='D',start='2014-01-01',end='2017-06-09')
szz=ts.get_k_data('399001', index=True,ktype='D',start='2014-01-01',end='2017-06-09')
fdc_index=ts.get_k_data('399241', index=True,ktype='D',start='2014-01-01',end='2017-06-09')


# 个股数据 万科 
wkA=ts.get_k_data('000002', index=False,autype='qfq',ktype='D',start='2014-01-01',end='2017-06-09')

#分行业
classified_stock=ts.get_industry_classified()
industy_names=list(classified_stock['c_name'].unique())

# 选择特定行业股票
real_estate_stocks=classified_stock[classified_stock['c_name']=='房地产']

'''
# 行业内进行指标筛选  数据质量太差没法做
# 季度指标： ROE 毛利率 主营业务收入 等等
首先剔除小于0的
然后 选出最大的并以其标准化为1 
对每个季度的情况这样处理并且按权重加总

然后对指标进行权重加总

最终排序筛选出最好的3-5只股票

就是利用 杜邦分析法


'''



#candi_ind_indx=real_estate_stocks[['code','c_name','name']]
#year=2016
#quarters=[1,2,3,4]
#for q in quarters:
#    fin_info_temp=pd.read_csv(path+'fin_info_'+str(year)+'_'+str(q)+'.csv',sep=',',header=0,index_col =0,encoding='utf-8')
#    fin_info_temp=candi_ind_indx.merge(fin_info_temp,left_on="name",right_on="name",how='left',suffixes=("","_y_del"))
#    fin_info_temp=fin_info_temp.drop_duplicates(subset=['name'], keep='first')
#    drop_cols = [col for col in fin_info_temp.columns if '_y_del' in col]
#    fin_info_temp.drop(drop_cols,axis=1, inplace=True)
#    fin_info_temp['date_n']=str(year)+"-"+str(q)
#    
#    if q==1:
#        candi_ind_data=fin_info_temp.copy(deep=True)
#    else:
#        candi_ind_data=candi_ind_data.append(fin_info_temp,ignore_index=True)
#   
#        









# 得到待选股票池