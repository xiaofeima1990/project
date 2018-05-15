# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 14:34:02 2017

@author: guoxuan

data merge for land market database operation
"""

import sqlite3
import os,copy
import pandas as pd


path="D:\\Box Sync\\DATAbase\\first land market\\"

read_file_list =os.listdir(path)


savefile=[]
for element in read_file_list:
    savefile.append(os.path.splitext(os.path.basename(element)))
    
    
def datafile_cate(path):
    savefile=[]
    read_file_list =os.listdir(path)
    
    for element in read_file_list:
        savefile.append(os.path.splitext(os.path.basename(element)))
    
    # year=savefile[1][0].split('-')
    # year[0]
    f_year=set()
    temp_list=[]
    f_name_cat={}
    for ele in savefile:

        year=ele[0].split('-')[0]
        f_year.add(year)

        
    for ele in f_year:
        for ele2 in savefile:
            if ele in ele2[0]:
                temp_list.append(ele2[0]+ele2[1])    
        f_name_cat[ele]=copy.copy(temp_list)
        temp_list=[]
    
    return f_name_cat
    
def merge_data(path,year,f_name_cat):
    
    file_list=f_name_cat[year]
    count=0
    try:
        for file_ele in file_list:
    
            temp_data_df = pd.read_csv(path+file_ele,delimiter='\t',encoding='GBK')
            print(temp_data_df.shape)
            ######
            # mege data
            ######
            if count==0:
                data_df=temp_data_df
            else:
                data_df=data_df.append(temp_data_df,ignore_index=True)
    
            count+=1
            
    except Exception as e:
        print('error: ',e)
        return False
    return data_df 

    


    
def output_sqlite(df,path,name):
    con = sqlite3.connect(path+'land.db')
    df.to_sql(name,con,if_exists='replace',chunksize=20000,index=False)
    con.close()


 
# merge data for 2010 2011 2012 2013 2014 2015


cat=datafile_cate(path)
years=list(cat.keys()) 
test_df=merge_data(path,'2011',cat)

land_test_df=test_df[test_df['土地用途'].str.contains('工业')]
                     
house_test_df=test_df[test_df['土地用途'].str.contains('房')]
house_test_df=house_test_df[house_test_df['行业分类'].str.contains('房地')]

                            
house_test_df.to_csv(path+'temp11house.csv',sep='\t',encoding='GBK',index=False)
land_test_df.to_csv(path+'temp11ind.csv',sep='\t',encoding='GBK',index=False)
#test_big_df.to_csv(path+'temp13big.csv',sep='\t',encoding='GBK',index=False)

                            