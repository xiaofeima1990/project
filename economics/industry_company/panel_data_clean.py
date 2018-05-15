# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 13:16:05 2016

this code file is aimed at reoranize the dataset into panel data
这个程序文件目的在于重整数据，整理成panel data 形式来为后续的计量回归做准备

数据库：全国工业企业数据库 1996-2008 


项目系列：

国企改制-央企与地方比较


环境：python3
数据库： mysql 自己构建

@author: guoxuan
"""

'''
主要基础变量：
企业基本信息
法人代码	     ID
法人单位	     firm
法人	          legal_entity_name
开业时间（年）	start_year
开业时间（月）	start_month
企业规模	     size_cat
职工人数	     num_worker
行业类别	     industry_cat
注册类型	     register_type
国家控股情况     soe_control

财务信息：
实收资本	            paidin_capital
其中：国家资本金	       state_capital
流动资产合计	            current_capital
固定资产合计	            fix_asset
其中：生产经营用	       oper_fix_asset

资产总计	            total_asset
流动负债合计	            current_debt
长期负债合计	            long_debt
负债合计	            total_debt
所有者权益合计	       total_equity
产品销售收入(主营业务收入) prime_oper_revenue
产品销售成本(主营业务成本) prime_oper_cost
其他业务利润	            other_profit
管理费用	            admini_expense
财务费用	            finan_expense
补贴收入	            subsidy
本年应付工资总额	       total_salary
本年应付福利费总额	       total_welfare

'''

'''
有效时间段：1998-2007

1. 提取一直持续的企业，并且剔除掉其中数据错误的企业（国有控股异常变动）
2. 分别提取期间改制的企业（clean_reform）、 央企 (central_soe)、 其他国企(other_soe)、民营企业(privat)
3. 提取基本信息、财务信息 以及回归变量
5. 输出

'''
## import package
import pandas as pd
import pymysql.cursors
import numpy as np

path="F://DATAbase//company//"


# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123456',
                             db='industy_company',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

mysql_cursor = connection.cursor()

'''
1 提取一直持续的企业并且剔除掉错误企业
操作：
数据库中提取每年数据，算出每年2002到2007年企业ID相同的ID数，剔除掉重复数据
--原始持续存在的企业
在一直持续的企业中，算出2002 soe_ratio>0.5 nsoe_ratio<=0.5 且到2007年soe_ratio<0.5 的
--清洁的改制企业
在一直持续的企业中，算出2002年 soe_ratio <0.5 2007年soe_ratio<0.5的企业
--清洁的私营企业
在一直持续的企业中，算出2002年soe_ratio>0.5 2007 soe_ratio>0.5 的企业
--未转制企业
在未转制的企业中：
soe_ratio==1
大型企业
登记注册类型11 110 151
隶属关系中属于中央 10
判定为央企

非央企的未转制企业则被认定为其他国企
 

'''

###-------------------------------------
## 数据库的选择
###-------------------------------------

database_flag=1 # 0 = 1998-2002 1=2002-2007 2=1998-2007-
def choose_year(database_flag):
    if database_flag==0:
        table_name=['qy1999','qy2000','qy2001','qy2002']
    elif database_flag==1:
        table_name=['qy2002',"qy2003","qy2004","qy2005","qy2006","qy2007",]
    else:
        table_name=['qy1998','qy1999','qy2000','qy2001','qy2002',"qy2003","qy2004","qy2005","qy2006","qy2007",'2008']
    
    
    if database_flag==0:
        years=['1998','1999','2000','2001','2002','2003']
    elif database_flag==1:    
        years=['2002','2003','2004','2005','2006','2007']
    else:
        years=['1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008']

    return (years,table_name)
    
    
(years,table_name)=choose_year(database_flag)
## ----------------------------------------------------
## 第一步 ： 提取 2002年-2007年一直存续的公司ID
## 提取2002年的数据
## 提取2007年的数据 merge 即可
## ----------------------------------------------------

select_col="select ID, paidin_capital, state_capital from "+table_name[0]
m_df_common=pd.read_sql(select_col,con = connection,)

for i in table_name:
    
    select_col="select ID, paidin_capital, state_capital from "+i
    df_temp=pd.read_sql(select_col,con = connection,)
    m_df_common=pd.merge(df_temp,m_df_common,on='ID')


common_ID=pd.DataFrame(m_df_common['ID'].unique())

common_ID.to_csv(path+'common_ID_2002.txt',header=None, index=False)

## ----------------------------------------------------
# result is 88348
## ----------------------------------------------------

## 

## ----------------------------------------------------
## 第二步 选出2002-2007 一直存续企业中 国有控股的企业数量
## soe_ratio = soe_capital / paidin capital
## soe_ratio>0.5
## ----------------------------------------------------
survival_ID=pd.read_csv(path+"common_ID_2002.txt",header=None)
survival_ID.rename(columns={survival_ID.columns[0]:"ID"},inplace=True)

select_col="select ID, paidin_capital, state_capital from "+table_name[0]+" where ID in ('"+"','".join(survival_ID['ID'])+"')"

df_first=pd.read_sql(select_col,con = connection,)

df_first['soe_ratio']=df_first['state_capital']/df_first['paidin_capital']

soe_first=df_first.loc[df_first['soe_ratio']==1,'ID']
soe_first=pd.DataFrame(soe_first.unique())

soe_first.to_csv(path+'ID_soe_2002.txt',header=None, index=False)

## ----------------------------------------------------
# result is 10559
## ----------------------------------------------------


## ----------------------------------------------------
## 第三步 提取soe_ratio单调非增的数据
## 构建转制企业数据信息
## 构建非转制企业数据信息
## ----------------------------------------------------


survival_ID=pd.read_csv(path+"ID_soe_2002.txt",header=None)
survival_ID.rename(columns={survival_ID.columns[0]:"ID"},inplace=True)


select_col="select ID, paidin_capital, state_capital from "+table_name[0]+" where ID in ('"+"','".join(survival_ID['ID'])+"')"

df_temp=pd.read_sql(select_col,con = connection,)
df_temp['soe_ratio']=df_temp['state_capital']/df_temp['paidin_capital']
df_temp.drop_duplicates(subset='ID',keep='first',inplace=True)

temp_df=pd.DataFrame()
temp_df['ID']=df_temp['ID'].copy()
temp_df['soe_ratio']=df_temp['soe_ratio'].copy()
for i in table_name:
    
    select_col="select ID, paidin_capital, state_capital from "+i+" where ID in ('"+"','".join(survival_ID['ID'])+"')"
    
    df_temp=pd.read_sql(select_col,con = connection,)
    df_temp.drop_duplicates(subset='ID',keep='first',inplace=True)    

    df_temp['paidin_capital']=pd.to_numeric(df_temp['paidin_capital'],errors='coerce')
    df_temp['state_capital']=pd.to_numeric(df_temp['state_capital'],errors='coerce')
    
    df_temp[i]=pd.to_numeric(df_temp['state_capital']/df_temp['paidin_capital'])
    temp_df=pd.merge(temp_df,df_temp[['ID',i]],on='ID')    

# test for random ID
temp_df.loc[temp_df['ID']=='63435090X',:]

temp_df=temp_df.dropna(axis=0,how='any')
## 取得一直非增的数据 2002 -- 2007
flag2=(temp_df['qy2007']>temp_df['qy2006'])|(temp_df['qy2006']>temp_df['qy2005'])|(temp_df['qy2005']>temp_df['qy2004'])|(temp_df['qy2004']>temp_df['qy2003'])|(temp_df['qy2003']>temp_df['qy2002'])
true_df2=temp_df.loc[~flag2,:]
true_df2=true_df2.dropna(axis=0,how='any')
## 剔除错误的结果 5915  原来的 7409

## 1998 年国企 


flag2=(temp_df['qy2003']>temp_df['qy2002'])|(temp_df['qy2002']>temp_df['qy2001'])|(temp_df['qy2001']>temp_df['qy2000'])|(temp_df['qy2000']>temp_df['qy1999'])
true_df2=temp_df.loc[~flag2,:]
true_df2=true_df2.dropna(axis=0,how='any')

c_soe_1998=true_df2.loc[true_df2['qy1998']==1,:]
c_soe_1998['ID'].to_csv(path+'vip_soe_1998.txt',header=None,index=False)


## 改制企业
c_reform_2003=true_df2.loc[true_df2['qy2003']<1,:]
c_reform_2003['ID'].to_csv(path+'1998_reform_clean.txt',header=None,index=False)


c_soe_2003=true_df2.loc[true_df2['qy2003']==1,:]
#c_soe_2002_total=true_df2.loc[true_df2['qy2002']>0.99,:]


## 2007 年 国有控股数据 
c_soe_2002=true_df2.loc[true_df2['qy2002']==1,:]
c_soe_2007=c_soe_2002.loc[c_soe_2002['qy2007']==1,:]
c_soe_2007['ID'].to_csv(path+'soe_2007_remain.txt',header=None,index=False)
##---------
## 结果 3997
## --------

## 2002 年 改制企业数据
c_reform_2007=c_soe_2002.loc[c_soe_2002['qy2007']<1,:]
c_reform_2007['ID'].to_csv(path+'soe_2007_reform.txt',header=None,index=False)
##---------
## 结果 1917
## --------


## 取得2002 - 2007 非增的数据

'''
### 第一种取法

col=df_basic.columns
flag=df_basic.loc[:,col[4:len(col)]].min(axis=1)
true_df1=df_basic.loc[flag>=0,:]
true_df1=true_df1.dropna(axis=0,how='any')

### 第二种取法
## get the monotone nonincreasing 
flag2=(temp_df['qy2007']>temp_df['qy2006'])|(temp_df['qy2006']>temp_df['qy2005'])|(temp_df['qy2005']>temp_df['qy2004'])|(temp_df['qy2004']>temp_df['qy2003'])|(temp_df['qy2003']>temp_df['qy2002'])
true_df2=temp_df.loc[~flag2,:]
true_df2=true_df2.dropna(axis=0,how='any')

# 第三种取法
flag3=(temp_df['qy2002']>=temp_df['qy2003']) & (temp_df['qy2003']>=temp_df['qy2004']) & (temp_df['qy2004']>=temp_df['qy2005']) & (temp_df['qy2005']>=temp_df['qy2006']) & (temp_df['qy2006']>=temp_df['qy2007'])
true_df3=temp_df.loc[flag3,:]

# 第四种取法
flag4=(temp_df['qy2002']>=temp_df['qy2003']) & (temp_df['qy2003']>=temp_df['qy2004']) & (temp_df['qy2004']>=temp_df['qy2005']) & (temp_df['qy2005']>=temp_df['qy2006']) & (temp_df['qy2006']>=temp_df['qy2007'])
true_df4=temp_df.loc[flag4,:]

#temp_df.dropna(axis=0,how='any',inplace=True)
## 获取 2002年是 国有控股的数据 ： 2002 soe_ratio >0.5
c_soe_2002=true_df2.loc[true_df2['qy2002']>0.5,:]
# c_soe_2002=true_df1.loc[true_df1['soe_ratio']>0.5,:]
c_soe_2002.to_csv(path+'ID_clean_soe_2002.txt',header=None, index=False)

## -------------------------------------------
## result 3778 2002年 soe >0.5
## -------------------------------------------

## 转制企业数据
c_prv_2007=true_df2.loc[true_df2['qy2007']<0.5,:]

c_soe_2007=c_soe_2002.loc[c_soe_2002['qy2007']>0.5,:]

'''

## ---------------------------------------------------
##  清理数据
## ---------------------------------------------------

## -----
## function
## -----



dict_size={
"大型":'1',
"特大型":'11',
"大一型":'12',
"大二型":'13',
"中型":'2',
"中一型":'21',
"中二型":'22',
"小型":'3', 
}

def transfer(data):
    if data in dict_size.keys():
        return dict_size[data]
    else:
        return 0

def transfer1(data):
    data=str(data)    
    if data in ['11','12','13','1'] :
        x=1
    elif data in ['2','21','22']:
        x=2
    elif data in['3','30']:
        x=3
    else:
        x=0
    return x

## ---------
## 循环回归 剔除不良数据
## ---------

## 导入ID 

clean_ID=pd.read_csv(path+"soe_2007_reform.txt",header=None)
temp_ID1=clean_ID.copy()
temp_ID1.rename(columns={temp_ID1.columns[0]:"ID"},inplace=True)


select_names=["ID","firm","industry_cat",'admin_code','belong_relation',
"register_type","start_year","start_month","num_worker",
"paidin_capital","state_capital",
"total_asset","fix_asset","oper_fix_asset",'total_profit',
"total_debt","current_debt","long_debt",
"total_equity","prime_oper_revenue","other_profit","bus_profit",
"prime_oper_cost","admini_expense","finan_expense",
"subsidy","total_salary","total_welfare",
'fix_asset_price','prime_oper_expense','prime_oper_tax','salary','welfare']+(database_flag==0)*['total_prod_p','new_prod']
#df_panel=pd.DataFrame(columns=select_names)

cols=",".join(select_names)


for year in years:
    table_name='qy'+year
    if year!='2004':
        cols_new=cols+",size_cat"
    else:
        cols_new=cols    
    
    select_cols="select "+cols_new+" from "+table_name+" where ID in ('"+"','".join(temp_ID1['ID'])+"')"
        
    
    df_basic=pd.read_sql(select_cols,con = connection,)
    df_basic.drop_duplicates(subset='ID',keep='first',inplace=True)
    
    if year =='2006' or year=='2007':
        temp=df_basic['size_cat'].apply(transfer)
        df_basic['size_cat']=temp.copy()
    elif year=='2004':
        df_basic=pd.merge(df_basic,temp_size,on="ID")        
    elif year=='2003':
        df_basic['size_cat']=df_basic['size_cat'].apply(transfer1)
        temp_size=df_basic[['ID','size_cat']]
    else:
        df_basic['size_cat']=df_basic['size_cat'].apply(transfer1)
           
    
#    if year=='2005':
#        df_basic.loc[df_basic['ID']=='214971152','total_asset']=59224
    ## 数据清理
    df_basic.dropna(axis=0,how='any',inplace=True)
    df_basic=df_basic.loc[df_basic['paidin_capital']>=0,:]
    df_basic['soe_ratio']=df_basic['state_capital']/df_basic['paidin_capital']
    df_basic['bus_profit']=df_basic['bus_profit'].astype(float)
    df_basic['prime_oper_revenue']=df_basic['prime_oper_revenue'].astype(float)
    df_basic=df_basic.loc[df_basic['prime_oper_revenue']>=0,:]
    df_basic['fix_asset']  =df_basic['fix_asset'].astype(float) 
    df_basic=df_basic.loc[df_basic['fix_asset']>=0,:]
    df_basic['oper_fix_asset']=df_basic['oper_fix_asset'].astype(float)
    df_basic=df_basic.loc[df_basic['oper_fix_asset']>=0,:] 
    df_basic['ROS']=df_basic['bus_profit']/(df_basic['prime_oper_revenue'])
    df_basic['oper_asset_ratio']=df_basic['oper_fix_asset']/df_basic['fix_asset']   
    df_basic['total_debt']=df_basic['total_debt'].astype(float)
    df_basic['total_asset']=df_basic['total_asset'].astype(float)
    df_basic=df_basic.loc[df_basic['total_asset']>0,:]
    df_basic['oper_fix_asset']=df_basic['oper_fix_asset'].astype(float)
    
    df_basic['admini_expense']=df_basic['admini_expense'].astype(float)
    df_basic=df_basic.loc[df_basic['admini_expense']>=0,:]    
    df_basic['leverage']=df_basic['total_debt']/df_basic['total_asset']
    df_basic=df_basic.loc[df_basic['leverage']>=0,:]
    df_basic=df_basic.loc[df_basic['subsidy']>=0,:]
    df_basic=df_basic.loc[df_basic['total_welfare']>=0,:]
    df_basic=df_basic.loc[df_basic['total_salary']>=0,:]
    df_basic=df_basic.loc[df_basic['soe_ratio']>=0,:]
    df_basic=df_basic.loc[df_basic['soe_ratio']<=1,:] 
    df_basic=df_basic.loc[df_basic['num_worker']>0,:]
    
       
    df_basic=df_basic.replace([np.inf, -np.inf], np.nan)
    df_basic.dropna(axis=0,how='any',inplace=True)

    temp_ID=df_basic['ID']
    temp_ID=pd.DataFrame(temp_ID)
      
        
    if  len(temp_ID['ID'])<len(temp_ID1['ID']):
        temp_ID1=temp_ID.copy()
#
## 确定 一共有多少 clean 的 企业数据
clean_total_ID=temp_ID1
clean_total_ID.to_csv(path+"soe_2007_reform.txt",header=None,index=False)

## 确定有多少国有控股企业
#
#year='2007'
#table_name='qy'+year
#if year!='2004':
#    cols_new=cols+",size_cat"
#else:
#    cols_new=cols  
#    
#select_cols="select "+cols_new+" from "+table_name+" where ID in ('"+"','".join(temp_ID1['ID'])+"')"
#    
#df_basic=pd.read_sql(select_cols,con = connection,)
#df_basic.drop_duplicates(subset='ID',keep='first',inplace=True)
#    
#df_basic['soe_ratio']=df_basic['state_capital']/df_basic['paidin_capital'] 
#df_basic.dropna(axis=0,how='any',inplace=True)
#
#index_soe=df_basic.loc[df_basic['soe_ratio']>0.5,'ID']
#index_soe.to_csv(path+"vip_soe_clean_final.txt",header=None,index=False)
#
#index_reform=df_basic.loc[df_basic['soe_ratio']<=0.5,'ID']
#index_reform.to_csv(path+"vip_reform_clean_final.txt",header=None,index=False)
#
#index_soe_1=df_basic.loc[df_basic['soe_ratio']>0.99,'ID']
#index_soe_1.to_csv(path+"vip_soe_1_clean_final.txt",header=None,index=False)
#
#index_soe_part=list(set(index_soe.values)-set(index_soe_1.values))
#index_soe_part=pd.Series(index_soe_part)
#index_soe_part.to_csv(path+"vip_soe_part_clean_final.txt",header=None,index=False)
### 央企的数量提取


def ID_filter(DF,col_name,condition,flag=0):
    # size
    if flag==0:
        DF[col_name]=pd.to_numeric(DF[col_name],errors='coerce')    

    temp_ID=DF.loc[DF[col_name]==condition,'ID']
    DF.set_index('ID',inplace=True)
    DF=DF.loc[temp_ID,:]
    DF.reset_index(inplace=True)
#    # 隶属关系
#    temp_ID=DF.loc[DF['belong_relation']=='10','ID']
#    DF.set_index('ID',inplace=True)
#    DF=DF.loc[temp_ID,:]
#    DF.reset_index(inplace=True)
#    
    return (DF,temp_ID)
    


###--------------------------------------------------------
### step 2  get the cancidate panel data
### 获取所想要的面板数据集合
###--------------------------------------------------------

final_ID=pd.read_csv(path+"soe_2007_reform.txt",header=None)
final_ID=pd.DataFrame(final_ID)
final_ID.rename(columns={final_ID.columns[0]:0},inplace=True)
#ID_list=tuple(final_ID[0])
#soe_ID=pd.read_csv(path+"final_ID_soe.txt",header=None)
final_ID=temp_ID.copy()

dict_size={
"大型":'1',
"特大型":'11',
"大一型":'12',
"大二型":'13',
"中型":'2',
"中一型":'21',
"中二型":'22',
"小型":'3', 
}

def transfer(data):
    if data in dict_size.keys():
        return dict_size[data]
    else:
        return 0

def transfer1(data):
    data=str(data)    
    if data in ['11','12','13','1'] :
        x=1
    elif data in ['2','21','22']:
        x=2
    elif data in['3','30']:
        x=3
    else:
        x=0
    return x



cols_num=["num_worker",
"paidin_capital","state_capital",
"total_asset","fix_asset","oper_fix_asset",'total_profit',
"total_debt","current_debt","long_debt",
"total_equity","prime_oper_revenue","other_profit","bus_profit",
"prime_oper_cost","admini_expense","finan_expense",
"subsidy","total_salary","total_welfare",
'fix_asset_price','prime_oper_expense','prime_oper_tax','salary','welfare']+(database_flag==0)*['total_prod_p','new_prod']
def clean_Data(DF,cols=cols_num):
    #转换成double
    for ele in cols:
        DF[ele]=pd.to_numeric(DF[ele],errors='coerce')
    
    ## 人均工资
    DF['ave_salary']=DF['total_salary']/(1+DF['num_worker'])
    ## 人均工资
    DF['ave_salary2']=DF['salary']/(1+DF['num_worker'])
    ## 人均福利
    DF['ave_welfare']=DF['total_welfare']/DF['num_worker']
    ## 人均福利
    DF['ave_welfare2']=DF['welfare']/DF['num_worker']
    ## 人均利润率
    DF['ave_profit']=DF['bus_profit']/DF['num_worker']
    ## 人均利润率
    DF['ave_profit2']=DF['total_profit']/DF['num_worker']
    
    ## 人均销售收入
    DF['ave_oper_revenue']=DF['prime_oper_revenue']/DF['num_worker']
    
    ## 人均销售成本
    DF['ave_oper_cost']=DF['prime_oper_cost']/DF['num_worker']
    
    ## ROA
    DF['ROA']=DF['bus_profit']/DF['total_asset']
    
    ## ROS      
    DF['ROS']=DF['bus_profit']/DF['prime_oper_revenue']
    
    ## ROA
    DF['ROA2']=DF['total_profit']/DF['total_asset']
    
    ## ROS sales
    DF['ROS2']=DF['total_profit']/(DF['prime_oper_revenue'])
    
    ## ROS sales
    DF['ROS2']=DF['total_profit']/(DF['prime_oper_revenue'])
    
    ## admini cost ratio
    DF['admini_cost_ratio']=DF['admini_expense']/(DF['prime_oper_revenue'])
    
    ## finance cost ratio
    DF['finan_expense_ratio']=DF['finan_expense']/(DF['prime_oper_revenue'])
    
    ## other profit ratio
    DF['other_profit_ratio']=DF['other_profit']/(DF['prime_oper_revenue'])
    
    
    ## leverage
    DF['leverage']=DF['total_debt']/DF['total_asset']
    
    ## production asset ratio
    DF['oper_asset_ratio']=DF['oper_fix_asset']/DF['fix_asset_price']
    
    ## log num_worker
    DF['lognum_worker']=np.log(DF['num_worker'])
    
    ## log total asset 
    DF['logasset']=np.log(1+DF['total_asset'])
    
    ## log total revenue
    DF['logrevenue']=np.log(1+DF['prime_oper_revenue'])
    
    ## subsidy
    DF['logsubsidy']=np.log(1+DF['subsidy'])    
    
    ## soe_ratio
    DF['nsoe_ratio']=1-DF['state_capital']/DF['paidin_capital']
    
    ## admin_code 
    DF['prov_code']=DF['admin_code'].str[0:3] 
    
    
    
    return DF.copy()
    
## 
def compute_HHI(DF):
    group_industry=DF.groupby('industry_code')
    HHI=pd.DataFrame(columns=['ID','HHI'])
    for name , sub_group in group_industry:
        temp=(sub_group['prime_oper_revenue']/sub_group['prime_oper_revenue'].sum())**2
        sub_group['HHI']=temp.sum()*10000    
        HHI=HHI.append(sub_group[['ID','HHI']])
    return HHI

def compute_rwoker(DF):
    group_industry=DF.groupby('industry_code')
    rworker=pd.DataFrame(columns=['ID','rworker'])
    for name , sub_group in group_industry:
        temp=(sub_group['prime_oper_revenue']/sub_group['prime_oper_revenue'].sum())*sub_group['num_worker'].sum()
        sub_group['rworker']=(sub_group['num_worker']-temp)/sub_group['prime_oper_revenue']
        rworker=rworker.append(sub_group[['ID','rworker']])
    return rworker

#
#select_names=["ID","firm","industry_cat",'admin_code','belong_relation',
#"register_type","start_year","start_month","num_worker",
#"paidin_capital","state_capital",
#"total_asset","fix_asset","oper_fix_asset",'total_profit',
#"total_debt","current_debt","long_debt",
#"total_equity","prime_oper_revenue","other_profit","bus_profit",
#"prime_oper_cost","admini_expense","finan_expense",
#"subsidy","total_salary","total_welfare",
#'fix_asset_price','prime_oper_expense','prime_oper_tax','salary','welfare','total_prod_p','new_prod']
##df_panel=pd.DataFrame(columns=select_names)
#
#cols=",".join(select_names)
#

'''
provicne deal with 

'''

prov=pd.read_csv(path+'province.txt',sep='\t',header=0)
prov.rename(columns={prov.columns[0]:"province"},inplace=True)
prov['code']=prov['code'].astype(str)
prov2code_dict=dict(zip(prov['province'],prov['code']))
code2prov_dict=dict(zip(prov['code'],prov['province']))


# 对admin_code 进行处理
prov_name=list(prov2code_dict.keys())
code_name=list(code2prov_dict.keys())
def code2prov(data):
    data=str(data)[0:2]
    temp_prov=[ prov for prov in code_name if data in prov]
    if len(temp_prov)>0:
        result=code2prov_dict[temp_prov[0]]
        
    else:
        result=''
    return result


## loop to construct the panel data 



for year in years:
    table_name1='qy'+year
        
    if year!='2004':
        cols_new=cols+",size_cat"
    else:
        cols_new=cols
    
        
    select_cols="select "+cols_new+" from "+table_name1+" where ID in ('"+"','".join(final_ID[0])+"')"
       
    
    df_basic=pd.read_sql(select_cols,con = connection,)
    df_basic.drop_duplicates(subset='ID',keep='first',inplace=True)
    if year=='2002':
        index=df_basic.loc[df_basic['num_worker']!=0,'ID']
        df_basic.set_index('ID',inplace=True)
        df_basic=df_basic.loc[index,:]
        df_basic.dropna(axis=0,how='any',inplace=True)   
        df_basic.reset_index(inplace=True)
        
    if year =='2006' or year=='2007':
        temp=df_basic['size_cat'].apply(transfer)
        df_basic['size_cat']=temp.copy()
    elif year=='2004':
        df_basic=pd.merge(df_basic,temp_size,on="ID")        
    elif year=='2003':
        df_basic['size_cat']=df_basic['size_cat'].apply(transfer1)
        temp_size=df_basic[['ID','size_cat']]
    else:
        df_basic['size_cat']=df_basic['size_cat'].apply(transfer1)

        
    df_clean=clean_Data(df_basic)
    df_clean['year']=year
    
    
#get provicne  info   
    df_clean['admin_code']=df_clean['admin_code'].astype(str)
    df_clean['prov']=df_clean['admin_code'].apply(code2prov)
    df_clean['prov_code']=df_clean['admin_code'].str[0:2]

# get industry code
    df_clean['industry_cat']=df_clean['industry_cat'].astype(str)
    df_clean['industry_code']=df_clean['industry_cat'].str[0:2]

    
# compute HHI
    temp_df=compute_HHI(df_clean[['ID','prime_oper_revenue','industry_code']])    
    df_clean=pd.merge(df_clean,temp_df,on="ID")    
    temp_df=compute_rwoker(df_clean[['ID','prime_oper_revenue','industry_code','num_worker']])
    df_clean=pd.merge(df_clean,temp_df,on="ID")     
    
#    temp=df_clean.loc[df_clean['nsoe_ratio']<=0.5,'ID']
#    df_clean.set_index('ID',inplace=True)
#    df_clean_c=  df_clean.loc[temp,:]
#    df_clean.reset_index(inplace=True)
#    df_clean_c.reset_index(inplace=True)
    
    if year ==years[0]:
        df_panel_total=df_clean.copy()
#        c_index=df_clean.loc[df_clean['nsoe_ratio']<=0.5,'ID']
#        df_clean.set_index('ID',inplace=True)
#        df_clean_c=  df_clean.loc[c_index,:]
#        df_clean.reset_index(inplace=True)
#        df_clean_c.reset_index(inplace=True)
#        df_panel_c=df_clean_c.copy()
    else:
        
        df_panel_total=df_panel_total.append(df_clean)
#        df_clean.set_index('ID',inplace=True)
#        df_clean_c=  df_clean.loc[c_index,:]
#        df_clean.reset_index(inplace=True)
#        df_clean_c.reset_index(inplace=True)
#        df_panel_c=df_panel_c.append(df_clean_c)



## save
#
#df_panel_c.to_sql('panel_change',con = connection,flavor='mysql',
#                  if_exists='replace',index=False,chunksize=5000)

df_panel_total.to_csv(path+"2002_panel_reform.csv",index=False,sep=",",header=True)

df_panel_c.to_csv(path+"panel_clean_reform.csv",index=False,sep=",",header=True)





## 数据清理：
for year in years:
    df_temp=df_panel_total.loc[df_panel_total['year']==year,:]
    df_temp=df_temp.loc[df_temp['rworker']<1,:]
#    df_temp=df_temp.loc[df_temp['HHI']<10000,:]
#    df_temp=df_temp.loc[df_temp['other_profit_ratio']<1,:]

    df_temp=df_temp.loc[df_temp['admini_cost_ratio']<5,:]
    df_temp=df_temp.loc[df_temp['admini_cost_ratio']>0,:]
    df_temp=df_temp.loc[df_temp['finan_expense_ratio']<5,:]
    df_temp=df_temp.loc[df_temp['finan_expense_ratio']>0,:]
    df_temp=df_temp.loc[df_temp['ROA']<1,:]
    df_temp=df_temp.loc[df_temp['ROS']<1,:]
    df_temp=df_temp.loc[df_temp['ROS']>-5,:]
    

        
    if year==years[0]:
        temp_ID=df_temp['ID']
        temp_ID=pd.DataFrame(temp_ID)
    else:
        temp_ID1=df_temp['ID']
        temp_ID1=pd.DataFrame(temp_ID1)
        temp_ID=pd.merge(temp_ID,temp_ID1,on='ID')
