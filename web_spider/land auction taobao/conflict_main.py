# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 10:32:04 2019

@author: gum27
this is to deal with conflict interest
"""

import pandas as pd
import sqlite3
import numpy as np


path_prefix = "C:\\Users\\gum27\\Documents\\gum27\\documentation\\"
store_path= "C:/Users/gum27/Documents/Dropbox/academic/11_work_dataset/justice auction/rawdata/"


con1 = sqlite3.connect(store_path+"auction_info_house.sqlite")
con2 = sqlite3.connect(store_path+"auction_info_house_conflict.sqlite")


con3 = sqlite3.connect(store_path+"auction_bidding_house.sqlite")
con4 = sqlite3.connect(store_path+"auction_bidding_house_conflict.sqlite")


# the conflict table names are 
# jinhua, ningbo, tianjin, yancheng, taizhou, shaoxing, wenzhou


tab_name=con1.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in tab_name:
    tab_name_list.append(name[0])
    

col_name = list(df_temp1.columns)
drop_col = []
for x in col_name:
    if "_y" in x:
        drop_col.append(x)

# revise 
df_temp1 = df_temp1.drop(drop_col, axis=1)
df_temp1 = df_temp1.drop(["index"], axis=1)
df_temp1 = df_temp1.rename(columns=lambda x: x[:-2])
df_temp1=df_temp1.rename(columns={"":"ID"})
df_temp1 = df_temp1.drop_duplicates("ID",keep="last")
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates("ID",keep="last")
df_append = df_append.drop(["index"], axis=1)

# jinhua_1 
df_temp2 = pd.read_sql("SELECT * FROM jinhua_1",con2)
df_temp2 = df_temp2.drop(["index"],axis = 1 )
df_temp2.to_sql("jinhua_1", con1, if_exists="replace")


# tianjin_1
df_temp1 = pd.read_sql("SELECT * FROM tianjin_1",con1)
df_temp2 = pd.read_sql("SELECT * FROM tianjin_1",con2)
df_temp1 = df_temp1.drop_duplicates("ID",keep="last")
df_temp2 = df_temp2.drop_duplicates("ID",keep="last")
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates("ID",keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con1, if_exists="replace")

# shaoxing 
table_name = "shaoxing_1"
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con2)
df_temp2 = df_temp2.drop_duplicates("ID",keep="last")
df_temp2 = df_temp2.drop(["index"], axis=1)
df_temp2.to_sql(table_name, con1, if_exists="replace")


# yancheng_1
table_name = "yancheng_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con1)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con2)
df_temp1 = df_temp1.drop_duplicates("ID",keep="last")
df_temp2 = df_temp2.drop_duplicates("ID",keep="last")
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates("ID",keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con1, if_exists="replace")


# taizhou
table_name = "taizhou_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con1)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con2)
df_temp1 = df_temp1.drop_duplicates("ID",keep="last")
df_temp2 = df_temp2.drop_duplicates("ID",keep="last")
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates("ID",keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con1, if_exists="replace")


# wenzhou
table_name = "wenzhou_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con1)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con2)
df_merge = df_temp1.merge(df_temp2, on = "ID", how = "outer")
df_merge = df_merge.loc[~pd.isnull(df_merge['ID']),]
df_merge.to_sql(table_name, con1, if_exists="replace")
df_temp2.to_sql(table_name, con1, if_exists="replace")


# ningbo
table_name = "ningbo_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con1)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con2)
df_temp1 = df_temp1.drop_duplicates("ID",keep="last")
df_temp2 = df_temp2.drop_duplicates("ID",keep="last")
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates("ID",keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con1, if_exists="replace")


con1.close()
con2.close()


"""
bidding part 

"""

# jinhua_1 
table_name = "jinhua_1"
#df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con3)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
df_temp2 = df_temp2.drop(["index"], axis=1)
df_temp2.to_sql("jinhua_1", con3, if_exists="replace")



# tianjin_1
table_name = "tianjin_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con3)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp1 = df_temp1.drop_duplicates(["ID_info","date","time"],keep="last")
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
print(len(df_temp2['ID_info'].unique()))
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates(["ID_info","date","time"],keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con3, if_exists="replace")


# shaoxing_1
table_name = "shaoxing_1"
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
print(len(df_temp2['ID_info'].unique()))
df_temp2 = df_temp2.drop(["index"], axis=1)
df_temp2.to_sql("shaoxing_1", con3, if_exists="replace")



# yancheng_1
table_name = "yancheng_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con3)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp1 = df_temp1.drop_duplicates(["ID_info","date","time"],keep="last")
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
print(len(df_temp2['ID_info'].unique()))
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates(["ID_info","date","time"],keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con3, if_exists="replace")


# taizhou
table_name = "taizhou_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con3)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp1 = df_temp1.drop_duplicates(["ID_info","date","time"],keep="last")
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
print(len(df_temp2['ID_info'].unique()))
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates(["ID_info","date","time"],keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con3, if_exists="replace")


# wenzhou
table_name = "wenzhou_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con3)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp1 = df_temp1.drop_duplicates(["ID_info","date","time"],keep="last")
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
print(len(df_temp2['ID_info'].unique()))
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates(["ID_info","date","time"],keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con3, if_exists="replace")


# ningbo
table_name = "ningbo_1"
df_temp1 = pd.read_sql("SELECT * FROM " + table_name,con3)
df_temp2 = pd.read_sql("SELECT * FROM " + table_name,con4)
df_temp1 = df_temp1.drop_duplicates(["ID_info","date","time"],keep="last")
df_temp2 = df_temp2.drop_duplicates(["ID_info","date","time"],keep="last")
print(len(df_temp1['ID_info'].unique()))
print(len(df_temp2['ID_info'].unique()))
df_append = df_temp1.append(df_temp2)
df_append = df_append.drop_duplicates(["ID_info","date","time"],keep="last")
df_append = df_append.drop(["index"], axis=1)
df_append.to_sql(table_name, con3, if_exists="replace")


con3.close()
con4.close()



## alter name 
con1 = sqlite3.connect(store_path+"auction_info_house.sqlite")

tab_name=con1.execute("SELECT name FROM sqlite_master WHERE type='table';")
tab_name_list=[]
for name in tab_name:
    tab_name_list.append(name[0])
    
jiangsu = ['nanjing','xuzhou','suzhou','wuxi','yancheng','zhenjiang','changzhou','nantong']
zhejiang = ['hangzhou','ningbo','quzhou','lishui','zhoushan','jinhua','wenzhou','taizhou']

sql_query = "ALTER TABLE `beijing_1` RENAME TO `beijing_bj_1`"

cursor      = con1.cursor()
for ele in zhejiang:
    renameTable = "ALTER TABLE " +ele + "_1" + " RENAME TO " + ele + "_zj_1"
    cursor.execute(renameTable)
    
# Save (commit) the changes
con1.commit()
con1.close()