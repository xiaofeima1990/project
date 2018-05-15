# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 20:38:51 2016

@author: guoxuan
this script is aimed at collecting basic operation for database 
mainly my databse is just mySQL and sqlite


mySQL is larger bigger 
but sqlite is more lighter and flexible 


"""


## import data from csv 
## one way to use sqlitebrowser or NaviSQL to import data
## another way is to use pandas 

import pandas as pd 
import os,glob
import sqlite3

path="G:\\database\\company_geo_clean\\"

## get all txt file in a dir
db_file=""
### method 1 
read_file_list =os.listdir(path)
file_list=[]
for file in read_file_list:
    if file.endswith(".txt"):
        file_list.append(file)
    if file.endswith(".db"):
        db_file=file
    
    
### method 2
read_file_list = glob.glob(path+'*.txt')
db_file=glob.glob(path+'*.db')
file_list=[x.split("\\")[-1] for x in read_file_list]

## current choose method 2 to use
conn = sqlite3.connect(db_file[0])
i=1
temp=pd.read_csv(read_file_list[i],sep="\t",encoding="utf-8",dtype=str)
table_name=file_list[i].split(".")[0]
temp.to_sql(table_name, conn, if_exists='replace', index=False)

