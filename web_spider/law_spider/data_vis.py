# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 21:29:13 2016

This script is aimed at visulizing the spider information 

@author: guoxuan
"""

import pandas as pd
import numpy as np
from spider_database import *
import jieba


## visualizing the data 
data_base=spider_database('spider_info.db','.\\data\\')
table_names=data_base.get_table_name()

col_name = data_base.get_col_name(table_names[1])

df=data_base.read_data(col_name,table_names[2])

cut_words=jieba.cut(df.loc[4,'court'])
for ele in cut_words:
    print(ele)

