# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 21:05:27 2016

@author: guoxuan


"""
import pandas as pd
import numpy as np

path="F://DATAbase//company//"



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
        years=['2002','2003','2004','2005','2006','2007','2008']
    else:
        years=['1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008']

    return (years,table_name)
    
def choose_database(database_flag):
    if database_flag==0:
        df_panel=pd.read_csv(path+"vip_1998_panel.csv",encoding='gbk')
        col_name=df_panel.columns
    else:
        df_panel=pd.read_csv(path+"vip_2003_short.csv",encoding='gbk')
        col_name=df_panel.columns
    return (df_panel, col_name)
    
    
(years,table_name)=choose_year(database_flag)
(df_panel, col_name)= choose_database(database_flag)

#DF = DF.drop('column_name', 1)

#final_ID=pd.read_csv(path+"1998_reform_clean2.txt",header=None)
#final_ID=pd.DataFrame(final_ID)
#final_ID.rename(columns={final_ID.columns[0]:"panelid"},inplace=True)

### 关心的指标
'''
企业信息
    企业ID： panelid
    法人代码：frdm
    法人名称: qymc
    年份:    year
    企业规模	     qygm
    职工人数	     cyrs
    行业类别	     hylb
    注册类型	     djzclx
    国有控股情况     gykgqk
    地区代码         dqdm
    两位数行业代码    ind2_gb02
    两位数行业名称    industry
    
财务信息
    主营收入  zysr
    主营业务收入 zyywsr (没啥用) 全是nan
    营业外收入 yywsr  空
    营业收入   yysr 重要 就这个
    营业利润   yylr
    利润总额   lrze
    主营成本   zycb废掉
    产品销售费用 cpxsfy
    产品销售成本 cpxscb
    产品销售税金及附加 cpxssjjfj
    产品销售利润 cpxslr
    
    其他利润   qtlr 空
    实收资本	     sszb       paidin_capital
    其中：国家资本金	gjzbj       state_capital
    流动资产合计	     ldzchj       current_capital
    固定资产合计	     gdzchj       fix_asset
    其中：生产经营用	scjyy       oper_fix_asset
    
    资产总计	   zczj         total_asset
    流动负债合计	   ldfzhj         current_debt
    长期负债合计	   cqfzhj         long_debt
    负债合计	   fzhj         total_debt
    所有者权益合计   syzqyhj       total_equity
    
    其他业务利润	            other_profit
    管理费用	   glfy        admini_expense
    财务费用	   cwfy        finan_expense
    补贴收入	   btsr        subsidy
    本年应付工资总额	 bnyfgzze      total_salary
    主营业务应付工资总额 zyywyfgzze
    
    本年应付福利费总额	 bnyfflfze     total_welfare
    主营业务应付福利费总额 zyywyfflfze
    应交所得税         yjsds
    税金              sjjg 空
    增值税            bnyjzzs
    
    总产值        gyzczxjxgd
    新产品        xcpcz

'''

cancidate_col=['panelid','frdm','qymc','year','qygm','dqdm','cyrs','hylb','djzclx','gykgqk','prov',
               'ind2_gb02','industry','zysr','yylr','lrze',
               'cpxsfy','cpxscb','cpxslr','cpxssjjfj','sszb','gjzbj','ldzchj','gdzchj','scjyy',
               'zczj','ldfzhj','cqfzhj','fzhj','syzqyhj','glfy','cwfy','btsr','bnyfgzze','zyywyfflfze',
               'zyywyfgzze','yjsds','bnyjzzs','bnyfflfze','xcpcz','gyzczxjxgd','id','hylb_ind3gb02','gdzcyjhj','yysr']
               
df_basic=df_panel[cancidate_col].copy()
df_basic['year']=df_basic['year'].astype(str)
#df_basic.to_csv(path+"vip_2003_short.csv",index=False)
## get the common ID 


for i in years:
    if i == years[0]:
        temp_ID=df_basic.loc[df_basic['year']==i,'panelid']
        temp_ID=pd.DataFrame(temp_ID)
    else:
        temp_t=df_basic.loc[df_basic['year']==i,'panelid']
        temp_t=pd.DataFrame(temp_t)
        temp_ID=pd.merge(temp_ID,temp_t,on='panelid')
        
common_ID=temp_ID.copy()
## select the cancidate panel data

## common ID
def get_panel_by_ID(df_basic,common_ID):
#    df_basic['year']=df_basic['year'].astype(str)
#    df_basic=df_basic.set_index('panelid')
#    df_basic=df_basic.reset_index()
    
    for i in years:
        temp_df=df_basic.loc[df_basic['year']==i,:]
        temp_df=temp_df.set_index('panelid')
        temp_df=temp_df.loc[common_ID['panelid'],:]
        temp_df=temp_df.reset_index()
        if i==years[0]:
            df_clean=temp_df.copy()
        else:
            df_clean=df_clean.append(temp_df, ignore_index=True)
        
    return df_clean
#df_basic=df_basic.loc[common_ID.values,:]


df_clean=get_panel_by_ID(df_basic,common_ID)
df_clean.loc[df_clean['yysr'].isnull(),'yysr'].shape
## get soe company
temp_df=df_clean.loc[df_clean['year']==years[0],:]
temp_df['soe']=temp_df['gjzbj']/temp_df['sszb']
temp_ID=temp_df.loc[temp_df['soe']==1,'panelid']
temp_ID=pd.DataFrame(temp_ID)


df_clean=get_panel_by_ID(df_clean,temp_ID)
'''
未完成部分：
理解 文章进行回归的区间和样本选择问题 1999-2002 2003 年的企业当作参照组 日了狗了

'''
## 剔除错误数据

df_clean['soe']=df_clean['gjzbj']/df_clean['sszb']

def clean_soe(df_clean,years):
    
    for i in range(len(years[0:-1])):
        temp_soe1=df_clean.loc[df_clean['year']==years[i],'soe'].copy()
        temp_soe1.fillna(2,inplace=True)        
        temp_soe2=df_clean.loc[df_clean['year']==years[i+1],'soe'].copy()
        temp_soe2.fillna(2,inplace=True)
        
        if i==0:
            flag=(temp_soe1>=temp_soe2)
            flag=flag.reset_index(drop=True)
        else:
            temp_flag=(temp_soe1>=temp_soe2)
            temp_flag=temp_flag.reset_index(drop=True)
            flag=flag&temp_flag
#    flag=pd.DataFrame(flag)
    temp_ID=df_clean.loc[df_clean['year']==years[0],['panelid','soe']]
    clean_ID=temp_ID.loc[flag.values,'panelid']
    return clean_ID
    
clean_ID=clean_soe(df_clean,years)
clean_ID=pd.DataFrame(clean_ID)
df_clean=get_panel_by_ID(df_clean,clean_ID)

## 获取改制的数据
## 改制企业数据
df_temp=df_clean.loc[df_clean['year']==years[-1],['panelid','soe']]
df_reform_ID=df_temp.loc[df_temp['soe']<1,'panelid']
df_remain_ID=df_temp.loc[df_temp['soe']==1,'panelid']
df_reform_ID=pd.DataFrame(df_reform_ID)
df_remain_ID=pd.DataFrame(df_remain_ID)

df_reform=get_panel_by_ID(df_clean,df_reform_ID)
df_remain=get_panel_by_ID(df_clean,df_remain_ID)
## 改制企业数据整理



def clean_data(df):
    
    for year in years:
        print(year)
        df_basic=df.loc[df['year']==year,:]
        if year!=years[0]:
            df_basic=df_basic.set_index('panelid')
            df_basic=df_basic.loc[temp_ID1['panelid'],:]
            df_basic=df_basic.reset_index()
        else:
            temp_ID1=df_basic['panelid'].copy()
            temp_ID1=pd.DataFrame(temp_ID1)
        
#        df_basic.drop_duplicates(subset='frdm',keep='first',inplace=True)
        if year==years[-1]:
            df_basic['scjyy'].fillna(0, inplace=True)        
        df_basic.dropna(axis=1,how='all',inplace=True)
        
        df_basic=df_basic.loc[df_basic['sszb']>=0,:]
        df_basic['soe_ratio']=df_basic['gjzbj']/df_basic['sszb']
        df_basic['yylr']=df_basic['yylr'].astype(float)
        df_basic['yysr']=df_basic['yysr'].astype(float)
        ##产品销售
#        if 'cpxscb' not in df_basic.columns:
#            df_basic['cpxscb']=0
#        df_basic=df_basic.loc[df_basic['cpxslr']>=0,:]        
#        df_basic=df_basic.loc[df_basic['cpxscb']>=0,:]   
#        df_basic=df_basic.loc[df_basic['cpxsfy']>=0,:]   
#        df_basic=df_basic.loc[df_basic['cpxssjjfj']>=0,:]  
#        df_basic['cpxssr']=df_basic['cpxslr']+df_basic['cpxscb']+df_basic['cpxssjjfj']+df_basic['cpxsfy']
        df_basic=df_basic.loc[df_basic['yysr']>=0,:]
        df_basic['gdzchj']  =df_basic['gdzchj'].astype(float) 
        df_basic=df_basic.loc[df_basic['gdzchj']>=0,:]
        
        df_basic=df_basic.loc[df_basic['soe_ratio']>=0,:]
        df_basic=df_basic.loc[df_basic['soe_ratio']<=1,:]         
        
        df_basic['scjyy']=df_basic['scjyy'].astype(float)
        df_basic=df_basic.loc[df_basic['scjyy']>=0,:] 
        df_basic['ROS']=df_basic['yylr']/(df_basic['yysr'])
#        df_basic['ROS2']=df_basic['yylr']/(df_basic['cpxssr'])        
        df_basic['oper_asset_ratio']=df_basic['scjyy']/df_basic['gdzchj']   
        df_basic['fzhj']=df_basic['fzhj'].astype(float)
        df_basic['zczj']=df_basic['zczj'].astype(float)
        df_basic=df_basic.loc[df_basic['zczj']>0,:]
        
        
        df_basic['glfy']=df_basic['glfy'].astype(float)
        df_basic=df_basic.loc[df_basic['glfy']>=0,:]    
        df_basic['leverage']=df_basic['fzhj']/df_basic['zczj']
        df_basic=df_basic.loc[df_basic['leverage']>=0,:]
        df_basic=df_basic.loc[df_basic['btsr']>=0,:]
        df_basic=df_basic.loc[df_basic['bnyfflfze']>=0,:]
        df_basic=df_basic.loc[df_basic['bnyfgzze']>=0,:]
        
        df_basic=df_basic.loc[df_basic['cyrs']>0,:]
        
           
        df_basic=df_basic.replace([np.inf, -np.inf], np.nan)
        df_basic.dropna(axis=0,how='any',inplace=True)
        
        temp_ID=df_basic['panelid']
        temp_ID=pd.DataFrame(temp_ID)
          
            
        if  len(temp_ID['panelid'])<=len(temp_ID1['panelid']):
            temp_ID1=temp_ID.copy()

    return temp_ID1

clean_ID=clean_data(df_reform)

df_reform=get_panel_by_ID(df_clean,clean_ID)

'''
企业信息
    企业ID： panelid
    法人代码：frdm
    法人名称: qymc
    年份:    year
    企业规模	     qygm
    职工人数	     cyrs
    行业类别	     hylb
    注册类型	     djzclx
    国有控股情况     gykgqk
    地区代码         dqdm
    两位数行业代码    ind2_gb02
    两位数行业名称    industry
'''

#cancidate_col=['panelid','frdm','qymc','year','qygm','dqdm','cyrs','hylb','djzclx','gykgqk','prov',
#               'ind2_gb02','industry','zysr','yylr','lrze',
#               'cpxsfy','cpxscb','cpxslr','cpxssjjfj','sszb','gjzbj','ldzchj','gdzchj','scjyy',
#               'zczj','ldfzhj','cqfzhj','fzhj','syzqyhj','glfy','cwfy','btsr','bnyfgzze','zyywyfflfze',
#               'zyywyfgzze','yjsds','bnyjzzs','bnyfflfze','xcpcz','gyzczxjxgd','id','hylb_ind3gb02','gdzcyjhj']
#   

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
cols=['cyrs','hylb','djzclx','prov',
               'ind2_gb02','zysr','yylr','lrze',
               'cpxsfy','cpxscb','cpxslr','cpxssjjfj','sszb','gjzbj','ldzchj','gdzchj','scjyy',
               'zczj','ldfzhj','cqfzhj','fzhj','syzqyhj','glfy','cwfy','btsr','bnyfgzze','zyywyfflfze',
               'zyywyfgzze','yjsds','bnyjzzs','bnyfflfze','xcpcz','gyzczxjxgd','hylb_ind3gb02','gdzcyjhj','yysr']
     

def compute_index(DF,cols=cols):

    #转换成double
    for ele in cols:
        DF[ele]=pd.to_numeric(DF[ele],errors='coerce')
    
    ## 人均工资
    DF['ave_salary']=DF['bnyfgzze']/(1+DF['cyrs'])
    
    ## 人均福利
    DF['ave_welfare']=DF['bnyfflfze']/DF['cyrs']

    ## 人均利润率
    DF['ave_profit']=DF['lrze']/DF['cyrs']
    
    ## 人均销售收入
    DF['ave_oper_revenue']=DF['yysr']/DF['cyrs']
    
    
    ## ROA
    DF['ROA']=DF['yylr']/DF['zczj']
    
    ## ROS      
    DF['ROS']=DF['yylr']/DF['yysr']
    
    ## ROS sales
    DF['ROA2']=DF['lrze']/(DF['zczj'])
    
    ## ROS sales
    DF['ROS2']=DF['lrze']/(DF['yysr'])
    
    ## admini cost ratio
    DF['admini_cost_ratio']=DF['glfy']/(DF['yysr'])
    
    ## finance cost ratio
    DF['finan_expense_ratio']=DF['cwfy']/(DF['yysr'])
    
    
    ## leverage
    DF['leverage']=DF['fzhj']/DF['zczj']
    
    ## production asset ratio
    DF['oper_asset_ratio']=DF['scjyy']/DF['gdzcyjhj']
    
    ## log cyrs
    DF['lognum_worker']=np.log(DF['cyrs'])
    
    ## log total asset 
    DF['logasset']=np.log(1+DF['zczj'])
    
    ## log total revenue
    DF['logrevenue']=np.log(1+DF['yysr'])
    
    ## subsidy
    DF['logsubsidy']=np.log(1+DF['btsr'])    
    
    ## soe_ratio
    DF['nsoe_ratio']=1-DF['gjzbj']/DF['sszb']
    
    ## new_prod_ratio
    DF['new_prod_ratio']=DF['xcpcz']/DF['gyzczxjxgd']
    
    return DF.copy()

df_reform=compute_index(df_reform)


def compute_HHI(DF):
    
    group_industry=DF.groupby('ind2_gb02')
    HHI=pd.DataFrame(columns=['panelid','HHI'])
    for name , sub_group in group_industry:
        temp=(sub_group['yysr']/sub_group['yysr'].sum())**2
        sub_group['HHI']=temp.sum()*10000    
        HHI=HHI.append(sub_group[['panelid','HHI']])
    return HHI

def compute_rwoker(DF):
    group_industry=DF.groupby('ind2_gb02')
    rworker=pd.DataFrame(columns=['panelid','rworker'])
    for name , sub_group in group_industry:
        temp=(sub_group['yysr']/sub_group['yysr'].sum())*sub_group['cyrs'].sum()
        sub_group['rworker']=(sub_group['cyrs']-temp)/sub_group['cyrs']
        rworker=rworker.append(sub_group[['panelid','rworker']])
    return rworker
df_reform['HHI']=0
df_reform['rworker']=0
#df_reform['year']=df_reform['year'].astype(str)

for year in years:
    temp_df=df_reform.loc[df_reform['year']==year,:]
    temp=compute_HHI(temp_df[['panelid','yysr','ind2_gb02']])
    df_reform.loc[df_reform['year']==year,'HHI']=temp['HHI']
    temp=compute_rwoker(temp_df[['panelid','yysr','cyrs','ind2_gb02']])
    df_reform.loc[df_reform['year']==year,'rworker']=temp['rworker']

#HHI_temp=compute_HHI(DF[['panelid','yysr','ind2_gb02']])    
#df_reform=pd.merge(df_reform,HHI_temp,on='panelid')
#

df_reform.to_csv(path+'vip_2002_reform_new.csv',index=False)

df_basic=pd.read_csv(path+'vip_1998_reform.csv',encoding='gbk')
#df_basic['qygm']=df_basic['qygm'].apply(transfer1)
#
df_reform['year']=df_reform['year'].astype(str)
#

clean_type=1

## 数据清理：
for year in years:
    df_temp=df_reform.loc[df_reform['year']==year,:]
    
#    df_temp=df_temp.loc[df_temp['HHI']<10000,:]
#    df_temp=df_temp.loc[df_temp['other_profit_ratio']<1,:]
    if clean_type==0:
        df_temp=df_temp.loc[df_temp['rworker']<1,:]
        df_temp=df_temp.loc[df_temp['rworker']>-1,:]
        df_temp=df_temp.loc[df_temp['admini_cost_ratio']<1,:]
        df_temp=df_temp.loc[df_temp['admini_cost_ratio']>0,:]
        df_temp=df_temp.loc[df_temp['finan_expense_ratio']<1,:]
        df_temp=df_temp.loc[df_temp['ROA']<1,:]
        df_temp=df_temp.loc[df_temp['ROA']>-1,:]
        df_temp=df_temp.loc[df_temp['ROS']<1,:]
        df_temp=df_temp.loc[df_temp['ROS']>-5,:]
#        df_temp=df_temp.loc[df_temp['ave_oper_revenue']<1000,:]
#        df_temp=df_temp.loc[df_temp['ave_oper_revenue']>0,:]
#        df_temp=df_temp.loc[df_temp['ave_welfare']<20,:]
#        df_temp=df_temp.loc[df_temp['ave_salary']<100,:]
    else:
        df_temp.rworker[df_temp['rworker']>1]=np.nan
        df_temp.rworker[df_temp['rworker']<-1]=np.nan
        df_temp.loc[df_temp['admini_cost_ratio']>1,'admini_cost_ratio']=np.nan
        df_temp.loc[df_temp['admini_cost_ratio']<0,'admini_cost_ratio']=np.nan
        df_temp.loc[df_temp['finan_expense_ratio']>1,'finan_expense_ratio']=np.nan
        df_temp.loc[df_temp['finan_expense_ratio']<0,'finan_expense_ratio']=np.nan
        df_temp.loc[df_temp['ROA']>1,'ROA']=np.nan
        df_temp.loc[df_temp['ROA']<-1,'ROA']=np.nan
        df_temp.loc[df_temp['ROS']>1,'ROS']=np.nan
        df_temp.loc[df_temp['ROS']<-5,'ROS']=np.nan
    if year==years[0]:
        temp_ID=df_temp['panelid']
        temp_ID=pd.DataFrame(temp_ID)
        temp_df=df_temp.copy()
    else:
        temp_ID1=df_temp['panelid']
        temp_ID1=pd.DataFrame(temp_ID1)
        temp_ID=pd.merge(temp_ID,temp_ID1,on='panelid')
        temp_df=temp_df.append(df_temp.copy(),ignore_index=True)


temp_df.to_csv(path+'vip_2002_reform_new4.csv',index=False)


df_reform2=get_panel_by_ID(df_reform,temp_ID)
df_reform2.to_csv(path+'vip_2002_reform_new.csv',index=False)


## DID 准备
## 区分出 各个年份改制的企业数量
df_reform=pd.read_csv(path+"vip_2002_reform_new4.csv",encoding='gbk')
df_reform['year']=df_reform['year'].astype(str)
df_reform['flag']=0
df_reform['flag_50']=0
year_xx=years[1:]
count_list=[]

def set_flag(df,ID,flag):
    df=df.set_index('panelid')    
    for year in years:
        df.loc[ID,'flag']=flag
    df=df.reset_index()
    return df.copy()
flag_list=[1,2,3,4,5,6]        
i=0
flag_50=0

for year in year_xx:
    
    df_temp=df_reform.loc[df_reform['year']==year,:]
    if  year==year_xx[0] :  
        if flag_50==0:  
            temp_ID=df_temp.loc[df_temp['nsoe_ratio']>0,'panelid']
        else:
            temp_ID=df_temp.loc[df_temp['nsoe_ratio']>0.5,'panelid']
        df_reform=set_flag(df_reform,temp_ID.values,flag_list[i])
        temp_ID1=temp_ID.copy()
        count_list.append(len(temp_ID1))
    else:
        if flag_50==0:  
            temp_ID=df_temp.loc[df_temp['nsoe_ratio']>0,'panelid']
        else:
            temp_ID=df_temp.loc[df_temp['nsoe_ratio']>0.5,'panelid']
        temp_list=set(temp_ID.values)-set(temp_ID1.values)
        count_list.append(len(temp_list))
        df_reform=set_flag(df_reform,temp_list,flag_list[i])
        temp_ID1=temp_ID.copy()
    i+=1

df_reform.to_csv(path+'vip_2002_reform_new4.csv',index=False)


df_group=df_reform.groupby('year')

var_col=['lognum_worker','ave_salary','ave_welfare',
         'ROA','ROS','ave_profit','ave_oper_revenue',
         'logasset','logrevenue',
         'admini_cost_ratio','finan_expense_ratio']
DID_treat_pd=pd.DataFrame(columns=var_col)
DID_control_pd=pd.DataFrame(columns=var_col)
flag_i=1
state_flag=0
for name , sub_group in df_group:
    print(name)
    if name!='2008':
    #    DID_pd=DID_pd.append(,ignore_index=True)
        if state_flag==0:
            temp=sub_group.loc[sub_group['flag']<=flag_i,var_col].mean(axis=0)
        else:
            temp=sub_group.loc[sub_group['flag']==ii,var_col].mean(axis=0)
        DID_treat_pd=DID_treat_pd.append(temp,ignore_index=True)
        print(temp)
        temp=sub_group.loc[sub_group['flag']==6,var_col].mean(axis=0)
        DID_control_pd=DID_control_pd.append(temp,ignore_index=True)
    else:
        pass
    flag_i+=1

DID_treat_pd.to_csv(path+"DID_treat.csv",index=False)
DID_control_pd.to_csv(path+"DID_control.csv",index=False)

## 单个period 的分别走势图
writer1 = pd.ExcelWriter(path+'DID_treat2.xlsx', engine='xlsxwriter')
writer2 = pd.ExcelWriter(path+'DID_control2.xlsx', engine='xlsxwriter')
for ii in range(1,7):
    DID_treat_pd=pd.DataFrame(columns=var_col)
    DID_control_pd=pd.DataFrame(columns=var_col)
    for name , sub_group in df_group:
        print(name)
        if name!='2008':
        #    DID_pd=DID_pd.append(,ignore_index=True)

            temp=sub_group.loc[sub_group['flag']==ii,var_col].mean(axis=0)
            DID_treat_pd=DID_treat_pd.append(temp,ignore_index=True)
            print(temp)
            temp=sub_group.loc[sub_group['flag']==6,var_col].mean(axis=0)
            DID_control_pd=DID_control_pd.append(temp,ignore_index=True)
        else:
            pass
        
    
    DID_treat_pd.to_excel(writer1,sheet_name=str(ii))
    DID_control_pd.to_excel(writer2,sheet_name=str(ii))

writer1.save()
writer2.save()


### 分地区 划分

east=(21,11,12,13,37,32,33,31,35,44,45,46)
middle=(14,15,22,23,34,36,41,42,43)
west=(61, 62, 63, 64, 65, 51, 50, 53,52,54)

def region(data):
  if int(data) in east:   
      return 1
  elif int(data) in middle:
      return 2
  else: 
      return 3

df_reform_1=df_reform.loc[df_reform['year']=='2003',:]  
df_remain_1=df_remain.loc[df_remain['year']=='2003',:]
df_reform_1['region']=df_reform_1['prov'].apply(region)
df_remain_1['region']=df_remain_1['prov'].apply(region)
dd_group=df_reform_1.groupby("region")
dd_group['panelid'].count()
dd2_group=df_remain_1.groupby("region")
dd2_group['panelid'].count()