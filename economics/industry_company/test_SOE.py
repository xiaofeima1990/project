# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 23:32:17 2016

此文件关注于工业企业数据 导入、数据库的构建和数据的清理


env：python3
@author: guoxuan
"""

import pandas as pd

import pymysql.cursors



#path="F://DATAbase//company//data//国泰安//"
#company_2007=pd.read_excel(path+"NLE_Basic_2008"+".xlsx")
path="F://DATAbase//company//"

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123456',
                             db='industy_company',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


# select columns from database 
select_cols="select * from qy04;"

df=pd.read_sql(select_cols,con = connection,)



'''
dataabse 操作示例
'''

mysql_cursor = connection.cursor()

sql_col_property="show columns from qy04"

mysql_cursor.execute(sql_col_property)

results = mysql_cursor.fetchall()

df_tpye=pd.DataFrame(results)



# 重命名列
sql="ALTER TABLE qy04 change code 法人代码  varchar(9)"
mysql_cursor.execute(sql)

connection.commit()


'''
数据整理

'''

## get tables name from database
try:
    mysql_cursor.execute('show tables')
    table_name= mysql_cursor.fetchall()
    table_name=pd.DataFrame(table_name)
except e:
    print(e)
    

#查看国有企业与非国有企业历年的占比
#select_col ="select 控股情况,机关级别,资产总计,实收资本,国家资本,开业时间（年） from"+ table_name
survival_ID=pd.read_csv(path+"common_ID.txt",header=None)
survival_ID.rename(columns={survival_ID.columns[0]:"ID"},inplace=True)
#survival_ID.set_index('ID',inplace=True)
tb_names=['qy02','qy03','qy04','qy05','qy06','qy07']
soe_ratio=pd.DataFrame(data=None,columns=['soe','nsoe'])

# 选取特定的列的名字
## 国有控股

for i in range(len(tb_names)):
    
    soe_col="select ID, soe_control from "+ tb_names[i]
    df_subset=pd.read_sql(soe_col,con = connection,)
    df_subset.set_index('ID',inplace=True)
    df_subset=df_subset.loc[survival_ID.ID,:]
    soe_group=df_subset.groupby('soe_control')
    soe_ratio.loc[i,:]=(soe_group['soe_control'].count()[0],soe_group['soe_control'].count()[1:3].sum())
    soe_ratio.loc[i,:]=soe_ratio.loc[i,:]/soe_ratio.loc[i,:].sum()
    

# 国有资产占比情况统计

for i in range(len(tb_names)):
    
    soe_col="select ID, paidin_capital, state_capital from "+ tb_names[i]
    df_subset=pd.read_sql(soe_col,con = connection,)
    df_subset.set_index('ID',inplace=True)
    df_subset=df_subset.loc[survival_ID.ID,:]
    temp_s=df_subset['state_capital']/df_subset['paidin_capital']
    soe_ratio.loc[i,:]=(temp_s[temp_s>0.5].count()/temp_s.count(),temp_s[temp_s<=0.5].count()/temp_s.count())

    

plot=soe_ratio['soe'].plot()
fig=plot.get_figure()
fig.savefig(path+'soe_ratio_change.png')



#SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'your database schema' AND TABLE_NAME = 'the wanted table name' AND ORDINAL_POSITION = 2;



'''
数据库清理

重命名
数据规整


'''

# 重命名 对国企控股 实收资本 国家资本 法人代码

names_select=["控股","实收资本","国家资本","法人代码"]
new_names=['soe_control','paidin_capital','state_capital',"ID"]
name_selct=names_select[2]
get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where COLUMN_NAME like '%"+name_selct+"%' order by TABLE_NAME"
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)
new_name=new_names[2]
for i in range(len(cols_name_spe)):
    
    change_col_name="ALTER TABLE "+cols_name_spe.loc[i,'TABLE_NAME']+" CHANGE "+cols_name_spe.loc[i,'COLUMN_NAME']+" "+new_name+" "+cols_name_spe.loc[i,'COLUMN_TYPE']
#sql="ALTER TABLE qy04 change code 法人代码  varchar(9)"
    mysql_cursor.execute(change_col_name)

get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = 'industy_company' AND COLUMN_NAME like '%"+new_name+"%' order by TABLE_NAME"  
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)

connection.commit()




# 选取一直存在的企业02-07

col_02="select ID from qy02"
df_02=pd.read_sql(col_02,con = connection,)

col_07="select ID from qy07"
df_07=pd.read_sql(col_07,con = connection,)
'''
## 这么做是有问题的！！！
ind = df_02.ID.isin(df_07.ID) & df_07.ID.isin(df_02.ID)
survial_ID=df_02.loc[ind,'ID']
survial_ID.to_csv(path+"common_ID.txt",index=False)
'''

'''
## merge 方法来做
选取共同元素
'''

ss=pd.merge(df_07,df_02,how="inner",on='ID')
s1=ss.ID.unique()

