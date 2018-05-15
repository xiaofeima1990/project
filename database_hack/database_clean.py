# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 16:48:29 2016

@author: guoxuan
数据库操作，数据清理

整理好可以进行计量分析的数据

1. 数据重命名
2. 重要数据提取
3. dummy variable 处理
4. 相关中间变量的计算



"""


import pandas as pd

import pymysql.cursors



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
数据库清理

重命名
数据规整


'''


# 重命名 对国企控股 实收资本 国家资本 法人代码

names_select_basic=["企业名称","法人代表","省地县码","行业代码","注册类型","企业规模","全部职工","省（自治区、直辖市）","开业时间（月）","工业增加值"]
new_names=['firm',"legal_entity_name",'admin_code','industry_cat',"register_type","size_cat","num_worker","province","start_month","indust_addvalue"]
i=9

name_selct=names_select_basic[i]
get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where COLUMN_NAME like '%"+name_selct+"%' order by TABLE_NAME"
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)
new_name=new_names[i]
for i in range(len(cols_name_spe)):
    
    change_col_name="ALTER TABLE "+cols_name_spe.loc[i,'TABLE_NAME']+" CHANGE "+cols_name_spe.loc[i,'COLUMN_NAME']+" "+new_name+" "+cols_name_spe.loc[i,'COLUMN_TYPE']
#sql="ALTER TABLE qy04 change code 法人代码  varchar(9)"
    mysql_cursor.execute(change_col_name)

get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = 'industy_company' AND COLUMN_NAME like '%"+new_name+"%' order by TABLE_NAME"  
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)

connection.commit()


# 重命名 对财务指标进行

names_select_finance=["资产合计","固定资产合计","生产经营用","流动负债合计","长期负债","负债合计","所有者权益合计","主营业务收入","管理费用","财务费用","营业利润","其他业务利润","补贴收入","本年应付工资总额","本年应付福利","产品销售成本"]
new_names=["total_asset","fix_asset","oper_fix_asset","current_debt","long_debt","total_debt","total_equity","prime_oper_revenue","admini_expense","finan_expense","bus_profit","other_profit","subsidy","total_salary","total_welfare","prime_oper_cost"]
i=15

name_selct=names_select_finance[i]
get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where COLUMN_NAME like '%"+name_selct+"%' order by TABLE_NAME"
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)
new_name=new_names[i]
for i in range(len(cols_name_spe)):
    
    change_col_name="ALTER TABLE "+cols_name_spe.loc[i,'TABLE_NAME']+" CHANGE "+cols_name_spe.loc[i,'COLUMN_NAME']+" "+new_name+" "+cols_name_spe.loc[i,'COLUMN_TYPE']
#sql="ALTER TABLE qy04 change code 法人代码  varchar(9)"
    mysql_cursor.execute(change_col_name)

get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = 'industy_company' AND COLUMN_NAME like '%"+new_name+"%' order by TABLE_NAME"  
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)

connection.commit()


# 重命名 其他指标

names_select_finance=[
'邮编','利润总额','增值税','省份','隶属关系','固定资产原价合计','产品销售费用','产品销售税金及附加','产品销售利润','主营业务应付工资总额','主营业务应付福利费总额',
'工业总产值（现价）','新产品产值'
]
new_names=['post_code','total_profit','value_add_tax','province','belong_relation','fix_asset_price','prime_oper_expense','prime_oper_tax',
'prime_oper_profit','salary','welfare','total_prod_p','new_prod']
j=12

name_selct=names_select_finance[j]
get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where COLUMN_NAME like '%"+name_selct+"%' order by TABLE_NAME"
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)
new_name=new_names[j]
for i in range(len(cols_name_spe)):
    
    change_col_name="ALTER TABLE "+cols_name_spe.loc[i,'TABLE_NAME']+" CHANGE "+cols_name_spe.loc[i,'COLUMN_NAME']+" "+new_name+" "+cols_name_spe.loc[i,'COLUMN_TYPE']
#sql="ALTER TABLE qy04 change code 法人代码  varchar(9)"
    mysql_cursor.execute(change_col_name)

get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = 'industy_company' AND COLUMN_NAME like '%"+new_name+"%' order by TABLE_NAME"  
mysql_cursor.execute(get_col_name)
cols_name_spe=mysql_cursor.fetchall()
cols_name_spe=pd.DataFrame(cols_name_spe)

connection.commit()




# 显示表中的列名

show_cols="show columns from qy2002"
mysql_cursor.execute(show_cols)
temp_df=mysql_cursor.fetchall()
temp_df=pd.DataFrame(temp_df)




## 单独更改列名

change_col_name="ALTER TABLE "+"qy2008"+" CHANGE "+"主营业务收入"+" "+new_name+" "+"double"
#sql="ALTER TABLE qy04 change code 法人代码  varchar(9)"
mysql_cursor.execute(change_col_name)


## 添加列

add_col="alter table qy1996 add column prov varchar(30)"
mysql_cursor.execute(add_col)


'''
更新数据库中的少部分的值 
'''
## 更新 公司规模 统一一下分类

# 读取数据

select_cols="select ID,size_cat from qy2007;"

df=pd.read_sql(select_cols,con = connection,)


dict_size={
"大型":1,
"特大型":11,
"大一型":12,
"大二型":13,
"中型":2,
"中一型":21,
"中二型":22,
"小型":30, 
}

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

df['size_n']=df['size_cat'].apply(transfer1)



query = """ UPDATE qy2005 SET total_asset = 59224 WHERE ID = 214971152 """
data=(59224,214971152)

for i in range(len(df)):
    data = (float(df.loc[i,"size_n"]),str(df.loc[i,"ID"]))
    mysql_cursor.execute(query,data)

 
    # accept the changes
    

connection.commit()



'''
下面则是如何更新msql列  非常重要啊

CREATE TEMPORARY TABLE your_temp_table LIKE your_table;

LOAD DATA INFILE '/tmp/your_file.csv'
INTO TABLE your_temp_table
FIELDS TERMINATED BY ','
(id, product, sku, department, quantity); 

UPDATE your_table
INNER JOIN your_temp_table on your_temp_table.id = your_table.id
SET your_table.quantity = your_temp_table.quantity;

DROP TEMPORARY TABLE your_temp_table;

'''

## 首先提取数据然后处理数据
## 1996-2003 admin_code  6 位
## 2004-2007 province    12 位

prov=pd.read_csv(path+'province.txt',sep='\t',header=0)
prov.rename(columns={prov.columns[0]:"province"},inplace=True)
prov['code']=prov['code'].astype(str)
prov2code_dict=dict(zip(prov['province'],prov['code']))
code2prov_dict=dict(zip(prov['code'],prov['province']))


## construct the province city county address index
address=pd.read_csv(path+'address.txt',sep='\t',header=0)
address.rename(columns={address.columns[0]:"code"},inplace=True)
address['county']=address['county'].str.strip()
address['code']=address['code'].astype(str)

## province
prov_flag=address['code'].str.contains(r"\d{2}0000")
prov_code=address.loc[prov_flag,'code'].str[0:2]
prov_name=address.loc[prov_flag,'county']
prov_df=pd.concat([prov_code,prov_name],axis=1)


city_flag=address['code'].str.contains(r"\d{4}00")
city_code=address.loc[city_flag&(~prov_flag),'code'].str[0:4]
city_name=address.loc[city_flag&(~prov_flag),'county']
city_df=pd.concat([city_code,city_name],axis=1)



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


#df_panel=pd.DataFrame(columns=select_names)

sql_create="CREATE TEMPORARY TABLE temp_prov (ID varchar(20), admin_code varchar(8), prov varchar(30)) "
mysql_cursor.execute(sql_create)

sql_load="LOAD DATA INFILE 'F:/DATAbase/company/prov.csv' INTO TABLE temp_prov FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' (ID, admin_code, prov)"
mysql_cursor.execute(sql_load)

sql_update="UPDATE qy1996 INNER JOIN temp_prov on temp_prov.ID = qy1996.ID SET qy1996.prov = temp_prov.prov"
mysql_cursor.execute(sql_update)


sql_drop='DROP TEMPORARY TABLE temp_prov'
mysql_cursor.execute(sql_drop)

connection.commit()


## 第一步成功
select_names=["ID","admin_code",'prov']
cols=",".join(select_names)
year=['1996','1997','1998','1999']

table_name='qy'+year[0]

select_cols="select "+cols+" from "+table_name
    
df_cc=pd.read_sql(select_cols,con = connection,)
df_cc['admin_code']=df_cc['admin_code'].astype(str)
df_cc['prov']=df_cc['admin_code'].apply(code2prov)

## 第二部
df_cc.to_csv(path+'prov.csv',sep=',',header=None,index=False,encoding='utf-8')




'''
删除列

'''

drop_col="alter table qy2002 drop 年2002"
mysql_cursor.execute(drop_col)



connection.close()


'''
下面展示如何载入大数据
'''



import pandas as pd

import sys
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
     
def load_large_dta(fname,path=path):                        
    dta_df=pd.read_stata(path+fname,iterator=True)
    df = pd.DataFrame()
    try:
            chunk = dta_df.get_chunk(100*1000)
            while len(chunk) > 0:
                df = df.append(chunk, ignore_index=True)
                chunk = dta_df.get_chunk(100*1000)
                print('.'),
                sys.stdout.flush()
    except (StopIteration, KeyboardInterrupt):
        pass
    
    print('\nloaded {} rows'.format(len(df)))
    return dta_df
    
dta_df=load_large_dta("panel1998-2008.dta")    