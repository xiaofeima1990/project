# -*- coding: utf-8 -*-
"""
Created on Sun May 20 14:29:14 2018

@author: gum27

first time second time auction analysis 
analyze the first time auction, second time auction price distribution
analyze the matching information about the bidder's watchers and bidding information
"""

import pandas as pd
import re
import copy

#path="X:/My Documents/guoxuanma/my paper/justice auction/data/"
path="E:/Dropbox/academic/ideas/IO field/justice auction/data/"

df_1=pd.read_csv(path+"xuzhou-1-sf.csv",sep="\t", encoding='utf-8')
df_2=pd.read_csv(path+"xuzhou-2-sf.csv",sep="\t", encoding='utf-8')


'''
clean the data 
'''

df_1['status2']=0
df_1.loc[df_1['status']=="done",'status2']=1
        
df_2['status2']=0
df_2.loc[df_2['status']=="done",'status2']=1
        
        
df_1['p_ratio']=df_1['win_bid']/df_1['eval_price']

df_2['p_ratio']=df_2['win_bid']/df_2['eval_price']




df_1_c=df_1[df_1['status2']==1]
df_2_c=df_2[df_2['status2']==1]

tail1=df_1_c['p_ratio'].quantile(.99)
  
 
df_1_c = df_1_c.loc[df_1_c['p_ratio']<=tail1,]
df_1_c = df_1_c.loc[df_1_c['p_ratio']>0.5,]
df_1_c = df_1_c.reset_index(drop=True)

tail2=df_2['p_ratio'].quantile(.99)
 
df_2_c=df_2_c.loc[df_2_c['p_ratio']<=tail2,]
df_2_c=df_2_c.loc[df_2_c['p_ratio']>0.5,]
df_2_c = df_2_c.reset_index(drop=True)


# get hist graph
df_1_c['p_ratio'].hist(color="#1f77b4",bins=25)
df_2_c['p_ratio'].hist(color="#ff7f0e",bins=25)
## this an other things awe can do is to match from 2 and 1 and check those matached ratio

'''
按注册人数分组

'''

group_df_1_c=df_1_c.groupby(["n_resigter"])
group_df_2_c=df_2_c.groupby(["n_resigter"])

# 1 register     
temp_hist_1_1=group_df_1_c.get_group(1)
temp_hist_1_1['p_ratio'].hist(color="#1f77b4",bins=25)       
         
temp_hist_2_1=group_df_2_c.get_group(1)
temp_hist_2_1['p_ratio'].hist(color="#1f77b4",bins=25)       

# 2 register
temp_hist_1_1=group_df_1_c.get_group(2)
temp_hist_1_1['p_ratio'].hist(color="#1f77b4",bins=25)       
        
temp_hist_2_1=group_df_2_c.get_group(2)
temp_hist_2_1['p_ratio'].hist(color="#1f77b4",bins=25)       

# 3 register
temp_hist_1_1=group_df_1_c.get_group(3)
temp_hist_1_1['p_ratio'].hist(color="#1f77b4",bins=25)       
        
temp_hist_2_1=group_df_2_c.get_group(3)
temp_hist_2_1['p_ratio'].hist(color="#1f77b4",bins=25)       

# 4 register
temp_hist_1_1=group_df_1_c.get_group(4)
temp_hist_1_1['p_ratio'].hist(color="#1f77b4",bins=25)       
        
temp_hist_2_1=group_df_2_c.get_group(4)
temp_hist_2_1['p_ratio'].hist(color="#1f77b4",bins=25)       

'''
按年数 
2014 
2015
2016
2017

'''

df_1_c_year=df_1_c.groupby(["year"])
df_2_c_year=df_2_c.groupby(["year"])      
             
        
temp_hist_1_1=df_1_c_year.get_group(2017)
temp_hist_1_1['p_ratio'].hist(color="#1f77b4",bins=25)    
     
temp_hist_2_1=df_2_c_year.get_group(2017)
temp_hist_2_1['p_ratio'].hist(color="green",bins=25)


            


'''
匹配 第一次第二次  
clean df_2 df_2 

'''

def clean_title(x):
    if "（一拍）" in x:
        x=x.replace("（一拍）","")
    elif re.search(r'（.*二.*）.*',x):
        x=x.replace(re.search(r'（.*二.*）.*',x).group(),"")
    elif re.search(r'（.*第.*次.*）.*',x):
        x=x.replace(re.search(r'（.*第.*次.*）.*',x).group(),"")
    elif re.search(r'.{1}第.*次.*',x):
        x=x.replace(re.search(r'.{1}第.*次.*',x).group(),"")
    elif re.search(r'.*二期.*',x):
        x=x.replace(re.search(r'.*二期.*',x).group(),"")
    elif "拍卖公告" in x:
        x=x.replace("拍卖公告","")
    else:
        x=x
    return x

def clean_title2(x):

    if re.search(r'房.*$',x):
        x=x.replace(re.search(r'房.*$',x).group(),"")
    elif re.search(r'一.*$',x):
        x=x.replace(re.search(r'一.*$',x).group(),"")
    elif re.search(r'^.*关于对',x):
        x=x.replace(re.search(r'^.*关于对',x).group(),"")
    elif re.search(r'^.*关于',x):
        x=x.replace(re.search(r'^.*关于',x).group(),"")

    else:
        x=x
    return x


#df_1["title_1"]=df_1["title"].apply(clean_title)
df_2["title_2"]=df_2["title"].apply(clean_title)
df_2["title_2"]=df_2["title_2"].apply(clean_title2)
df_2["title_2"]=df_2["title_2"].apply(clean_title2)       
df_1['flag_match']=0

col_new_name1={
        "ID":"ID_1",
        "num_bids":"num_bids_1",
        "win_bid":"win_bid_1",
        "eval_price":"eval_price_1",
        "n_watch":"n_watch_1",
        "n_resigter":"n_resigter_1",
        "date":"date_1",
        "year":"year_1",
        "p_ratio":"p_ratio_1",
        "url":"url_1",
        
        }


col_new_name2={
        "ID":"ID_2",
        "num_bids":"num_bids_2",
        "win_bid":"win_bid_2",
        "eval_price":"eval_price_2",
        "n_watch":"n_watch_2",
        "n_resigter":"n_resigter_2",
        "date":"date_2",
        "year":"year_2",
        "p_ratio":"p_ratio_2",
        "url":"url_2",
        "title":"title_2",
        }





flag=1
for index, row in df_2.iterrows():
    temp_flag=row['title_2']
    # first time auction
    temp_s1=df_1.loc[df_1['title'].str.contains(temp_flag,regex=False),['ID','url', 'num_bids', 'win_bid', 'eval_price', 'n_watch',
       'n_resigter','title', 'date', 'year']]
    if temp_s1.empty:
        continue
    
    temp_s1=temp_s1.rename(columns=col_new_name1)
    temp_s1.reset_index(inplace=True,drop=True)
    temp_s1=temp_s1.iloc[0,:]
    
    
    # second time auction
    
    temp_s2=pd.DataFrame(row[['ID','url', 'num_bids', 'win_bid', 'eval_price', 'n_watch',
       'n_resigter','title', 'date', 'year']])
    temp_s2=temp_s2.T
    temp_s2=temp_s2.rename(columns=col_new_name2)
    temp_s2.reset_index(inplace=True,drop=True)
    temp_s2=temp_s2.iloc[0,:]
    
    # combine together 
    temp_df=pd.concat([temp_s1, temp_s2])
    temp_df=pd.DataFrame(temp_df)
    temp_df=temp_df.T
    
    # append
    if flag==1:
        match_df=temp_df.copy()
        flag=0
    else:
        match_df=match_df.append(temp_df,ignore_index=True)
        
    


# then we can get the information for matching 
    
match_df.to_csv(path+"match_xuzhou"+'.csv', sep='\t', encoding='utf-8',index=False)
    
    

match_df_cc=match_df[match_df['num_bids_2']>0]    
match_df_cc['price_ratio_2']=match_df_cc['win_bid_2']/match_df_cc['eval_price_2']    
tail=match_df_cc['price_ratio_2'].quantile(.99)
 
match_df_cc=match_df_cc.loc[match_df_cc['price_ratio_2']<=tail,]
match_df_cc=match_df_cc.loc[match_df_cc['price_ratio_2']>0,]


match_df_cc_g=match_df_cc.groupby(["num_bids_2"])
match_df_cc_g1=match_df_cc_g.get_group(1)
match_df_cc_g1=match_df_cc_g1[['price_ratio_2','year_2','ID_1','ID_2']]  



match_df_cc_g1['price_ratio_2'].plot.kde()  