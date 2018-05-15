# -*- coding: utf-8 -*-
"""
Created on Mon May 30 22:40:13 2016

@author: xiaofeima 

this script is aimed at craeting a main draft for webspider sql operation, which facilitate the 
data storage 

"""

   
'''
-----------
sqlite3 hacker start
-----------
'''


import pandas as pd
import sqlite3
import datetime
#path="E:\\"
#database_name="abs_info.db"

class spider_database():
    
    
    def __init__(self,database_name,path=""):
        self.path=path
        self.database_name=database_name
        self.conn = sqlite3.connect(path+database_name)
        self.c = self.conn.cursor()
        self.table_flag=0

    def creat_table(self, table_name,cols_name):
        '''
        table_name is string
        cols_name is dict contains the column name and property 
        like: "href":"text",
        '''        
        
        self.table_name=table_name
        name_par=[key +" "+ value for key, value in cols_name.items()]

        self.table_col=",".join(x for x in name_par)

        self.col_name= [key  for key in cols_name.keys()]
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS %s
             (%s)''' %(self.table_name,self.table_col))
        self.conn.commit()
        self.table_flag=1
        
    def save_data(self,chunk_dict):
        sql_insert="insert or ignore into %s (%s) values(:%s)" %(self.table_name,", ".join(x for x in self.col_name ), ", :".join(x for x in self.col_name ))
        try:        
            self.c.executemany(sql_insert, chunk_dict)
            self.conn.commit()
            print('%s data saved' %self.table_name)
        except sqlite3.IntegrityError:
            print("Record already exists")
        
        
    def read_data(self,col_name,table_name):
        select_cols="select %s from %s;" %(", ".join(x for x in col_name),table_name)
        df=pd.read_sql(select_cols,con = self.conn,)
        return df
    def close(self):
        self.conn.close()
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.path+self.database_name)
            self.c = self.conn.cursor()
        except Exception as e:
            print(e)
    def get_table_name(self):
        name_list=self.c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        self.table_names=[x[0] for x in name_list]
        return [x[0] for x in name_list]
    def get_col_name(self,table_name):
#        name_list=self.c.execute('show columns from '+table_name).fetchall()[0]
        name_list=self.c.execute('select * from '+table_name)  
        self.col_name=[x[0] for x in name_list.description]
        return [x[0] for x in name_list.description]
    
    def change_col_name(self,old_col_name,new_col_name,table_name,property_col='varchar(10)'):
        '''
        change the column name from selected table        
        property_col can have double, varchar(9)
        '''
        query="ALTER TABLE "+table_name+" CHANGE "+old_col_name+" "+new_col_name+" "+property_col
        try:         
            self.c.execute(query)
        except Exception as e:
            print(e)
        
        get_col_name="select * from INFORMATION_SCHEMA.COLUMNS where TABLE_SCHEMA = ' "+table_name+"' AND COLUMN_NAME like '%"+new_col_name+"%' order by TABLE_NAME"  
        new_col_list=self.c.execute(get_col_name).fetchall()
        return pd.DataFrame(new_col_list)

    def __del__(self):
        self.conn.close()
        

        

        


#for row in c.execute("select %s from abs_info" %", ".join(x for x in col_name )):
#    print(row)
#

## copy one table into another

type_str = type('str')
type_datetime = type(datetime.datetime.now())
type_int = type(1)
type_float = type(1.0)
type_None = type(None)
 
 
#todo: handle blob data type
 
def convert2str(record):
    res = []
    for item in record:
        if type(item)==type_None:
            res.append('NULL')
        elif type(item)==type_str:
            res.append('"'+item+'"')
        elif type(item)==type_datetime:
            res.append('"'+str(item)+'"')
        else:  # for numeric values
            res.append(str(item))
    return ','.join(res)
 
 
 
def copy_table(tab_name, src_cursor, dst_cursor):
    sql = 'select * from %s'%tab_name
    src_cursor.execute(sql)
    res = src_cursor.fetchall()
    cnt = 0
    for record in res:
        val_str = convert2str(record)
        try:
            sql = 'insert into %s values(%s)'%(tab_name, val_str)
            dst_cursor.execute(sql)
            cnt += 1
        except:
            print(cnt, val_str)
    return cnt
