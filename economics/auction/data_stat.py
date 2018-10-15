# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 13:42:59 2018

@author: xiaofeima

Data Statistics Summary


1. Number of bidders

2. Number of successful auction

3. The winning bid and evaluation price 

4. The distribution of winning bid 

5. prioroity bidder statistics mean use more data 

the prioroity bidder 
Average bidding round (period) not yet  

"""


# package 
import sqlite3
import pandas as pd
import numpy as np
import time, re,copy
import matplotlib.pyplot as plt

# path 
link_path="E:/auction/link/"

store_path="E:/auction/"



## connect to the sqlite
#con = sqlite3.connect(store_path+"auction_info.sqlite")

# general information for the auction 
con = sqlite3.connect(store_path+"auction_info.sqlite")

# bidding path for each auction
con1 = sqlite3.connect(store_path+"auction_bidding_1_land.sqlite")
con2 = sqlite3.connect(store_path+"auction_bidding_2_land.sqlite")



# Load the data into a DataFrame
df_1 = pd.read_sql_query("SELECT * from xuzhou_1", con)
df_2 = pd.read_sql_query("SELECT * from xuzhou_2", con)

con.close()


'''
number of bidders

'''
necessary_col=['index','num_bidder','n_register','priority_people','reserve_price','win_bid','evaluation_price']

# exclude the extreme value
tail1=df_1['num_bidder'].quantile(.99)

df_1_c=df_1.loc[df_1['num_bidder']<tail1,]
df_1_c=df_1_c.loc[df_1['num_bidder']>0,]
h1=df_1_c['num_bidder'].hist(color="#1f77b4",bins=25)
h1.set_xlabel("number of bidder")
h1.get_figure()

tail1=df_2['num_bidder'].quantile(.99)

df_2_c=df_2.loc[df_2['num_bidder']<tail1,]
df_2_c=df_2_c.loc[df_2['num_bidder']>0,]
h2=df_2_c['num_bidder'].hist(color="#1f77b4",bins=25)
h2.set_xlabel("number of bidder")
h2.get_figure()


      
      
'''
num of successful auction

'''

df_1_c=df_1[df_1['status']=='done']
df_2_c=df_2[df_2['status']=="done"]

print("total auctions in xuzhou first time auction: ",len(df_1))
print("total auctions in xuzhou second time auction: ",len(df_2))

print("total auctions in xuzhou first time auction: ",len(df_1_c))
print("total auctions in xuzhou second time auction: ",len(df_2_c))


'''
------------------------
Winning Bid Related 
------------------------

test for the high concentration first
filter those wrong data : eg. reserve > eval not those reserv/ eval < 80% in first stage 

define index : 
    p_res_eva = reserve / eva
    resev_proxy = |(win_bid - reserve)/ reserv|

'''
necessary_col=['index','num_bidder','n_register','priority_people','reserve_price','win_bid','evaluation_price','delay_count']

## check the reserve price situation


df_1_c['p_res_eva']=df_1_c['reserve_price']/df_1_c['evaluation_price']
df_2_c['p_res_eva']=df_2_c['reserve_price']/df_2_c['evaluation_price']


df_1_c['resev_proxy'] = (df_1_c['win_bid']-df_1_c['reserve_price'])/df_1_c['reserve_price']
df_2_c['resev_proxy'] = (df_2_c['win_bid']-df_2_c['reserve_price'])/df_2_c['reserve_price']

#df_1.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)
#df_2.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)

tail1=df_1_c['resev_proxy'].quantile(.99) 
tail2=df_2_c['resev_proxy'].quantile(.99) 



df_1_done=df_1_c.loc[df_1_c['resev_proxy']<tail1,['p_res_eva','resev_proxy']+necessary_col]
df_2_done=df_2_c.loc[df_2_c['resev_proxy']<tail2,['p_res_eva','resev_proxy']+necessary_col]

tail1=df_1_done['num_bidder'].quantile(.99) 
tail2=df_2_done['num_bidder'].quantile(.99) 

df_1_done=df_1_done.loc[df_1_done['num_bidder']<tail1,]
df_2_done=df_2_done.loc[df_2_done['num_bidder']<tail2,]

tail1=df_1_done['p_res_eva'].quantile(.99) 
tail2=df_2_done['p_res_eva'].quantile(.99) 
df_1_done=df_1_done.loc[df_1_done['num_bidder']<tail1,]
df_2_done=df_2_done.loc[df_2_done['p_res_eva']<tail2,]

#fig=df_1_done.plot.scatter(x="num_bidder",y='resev_proxy',c=df_1_done['index'],colormap='viridis')
#fig.set_xlabel("number of bidder")
#fig.set_ylabel("winning price premium")


# draw the scatter graph 
# x -> number of bidders
# y -> winning premium
# size -> delay count (approximate the number of bidding)
# color -> the reserve / eva 


plt.scatter(x=df_1_done["num_bidder"], y=df_1_done['resev_proxy'], s=df_1_done['delay_count'], c=df_1_done['p_res_eva'],
            alpha=0.5)

plt.xlabel("number of bidder")
plt.ylabel("winning price premium")
cax = plt.axes([0.95, 0.1, 0.05, 0.8])
plt.colorbar(cax =cax )
plt.show()

plt.scatter(x=df_2_done["num_bidder"], y=df_2_done['resev_proxy'], s=df_2_done['delay_count'], c=df_2_done['p_res_eva'],
            alpha=0.5)

plt.xlabel("number of bidder")
plt.ylabel("winning price premium")
cax = plt.axes([0.95, 0.1, 0.05, 0.8])
plt.colorbar(cax =cax )
plt.show()


'''
winning bid distrbution across the item value 
 p_ratio = winning / reserve

draw the scatter historgam
'''

df_1_c['p_ratio']=df_1_c['win_bid']/df_1_c['reserve_price']
df_2_c['p_ratio']=df_2_c['win_bid']/df_2_c['reserve_price']
df_1_c['p_ratio1']=df_1_c['win_bid']/df_1_c['evaluation_price']
df_2_c['p_ratio1']=df_2_c['win_bid']/df_2_c['evaluation_price']

tail1=df_1_c['p_ratio'].quantile(.99) 
tail2=df_1_c['p_ratio'].quantile(.99) 

df_1_done=df_1_c.loc[df_1_c['p_ratio']<tail1,['p_ratio','p_ratio1']+necessary_col]
df_2_done=df_2_c.loc[df_2_c['p_ratio']<tail2,['p_ratio','p_ratio1']+necessary_col]


tail1=df_1_done['num_bidder'].quantile(.99) 
tail2=df_2_done['num_bidder'].quantile(.99) 


df_1_done=df_1_done.loc[df_1_done['num_bidder']<tail1,]
df_2_done=df_2_done.loc[df_2_done['num_bidder']<tail2,]

tail1=df_1_c['p_ratio1'].quantile(.99) 
tail2=df_1_c['p_ratio1'].quantile(.99) 

df_1_done=df_1_done.loc[df_1_done['p_ratio1']<tail1,]
df_2_done=df_2_done.loc[df_2_done['p_ratio1']<tail2,]


# scatter hist !


from matplotlib.ticker import NullFormatter
nullfmt = NullFormatter()         # no labels

left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left + width + 0.05

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]


plt.figure(1, figsize=(8, 8))


axScatter = plt.axes(rect_scatter)
axHistx = plt.axes(rect_histx)
axHisty = plt.axes(rect_histy)

# no labels
#axHistx.xaxis.set_major_formatter(nullfmt)
#axHisty.yaxis.set_major_formatter(nullfmt)

x = df_1_done['num_bidder']
y = df_1_done['p_ratio1']

# the scatter plot:
axScatter.scatter(x, y)


lim1=df_1_done['num_bidder'].max()
lim2=df_1_done['p_ratio1'].max()
binwidth1= (lim1/20) 
binwidth2= (lim2/20) 
axScatter.set_xlim((0, lim1))
axScatter.set_ylim((0, lim2))

bin1 = np.arange(0, lim1+binwidth1, binwidth1)
bin2 = np.arange(0, lim2+binwidth2, binwidth2)


axHistx.hist(x, bins=bin1,rwidth=0.8 )
axHisty.hist(y, bins=bin2, orientation='horizontal',rwidth=0.8)

axHistx.set_xlim(axScatter.get_xlim())
axHisty.set_ylim(axScatter.get_ylim())
axScatter.set_xlabel("number of bidder")
axScatter.set_ylabel("winning bid over evaluation price")
plt.show()




# see the concentration around reserve price 

df_1_done_1=df_1_done.loc[df_1_done['p_res_eva']<=1,]
df_1_pic1=df_1_done_1.loc[df_1_done_1['resev_proxy']<0.01,]

df_1_pic1['resev_proxy'].hist()
df_1_pic1.plot.scatter(x="num_bidder",y='resev_proxy',s=df_1_pic1['index']*10)

df_2_done_1=df_2_done.loc[df_2_done['p_res_eva']<=1,]
df_2_pic1=df_2_done_1.loc[df_2_done_1['resev_proxy']<0.01,]

df_2_pic1['resev_proxy'].hist()
df_2_pic1.plot.scatter(x="num_bidder",y='resev_proxy',s=df_1_pic1['index']*10)






'''
priority people

try to find out something abnormal
Actually not, there are too few priority_people

'''

df_1_s=df_1.loc[df_1['status']=='done',]
df_2_s=df_2.loc[df_2['status']=='done',]


col_name= ['index', 'ID','n_register','reserve_price','p_res_eva', 'resev_proxy','num_bidder','priority_people','status', 'win_bid',]



df_1_s=df_1_s.loc[df_1_s['p_res_eva']<=1,col_name]
df_1_s=df_1_s.loc[df_1_s['p_res_eva']>=0.7,]
df_1_s=df_1_s.loc[df_1_s['num_bidder']>1,]
df_1_s=df_1_s.loc[df_1_s['resev_proxy']>0.01,]


df_2_s=df_2_s.loc[df_2_s['p_res_eva']<=1,col_name]
df_2_s=df_2_s.loc[df_2_s['p_res_eva']>=0.6,]
df_2_s=df_2_s.loc[df_2_s['num_bidder']>1,]
df_2_s=df_2_s.loc[df_2_s['resev_proxy']>0.01,]




# priority for succesful bid 
group_df_1_s=df_1_s.groupby(["priority_people"])

group_df_1_s.median()
group_df_1_s.mean()


pri_df_s = group_df_1_s.get_group(1)
nopri_df_s = group_df_1_s.get_group(0)

group_df_2_s=df_2_s.groupby(["priority_people"])

pri_df_s1 = group_df_2_s.get_group(1)
nopri_df_s1 = group_df_2_s.get_group(0)



# priority for all bid 

group_df_1=df_1.groupby(["priority_people"])

pri_df= group_df_1.get_group(1)
nopri_df= group_df_1.get_group(0)

group_df_2=df_2.groupby(["priority_people"])

pri_df2= group_df_2.get_group(1)
nopri_df2= group_df_2.get_group(0)








'''
conditional on years and number of bidders and reserve / evalutaion price ratios 
compre the winning bid ratio

'''




'''
check how many winning bids in stage 2 auction exceed the stage 1 reserve price / eva price
first thing is to build the connection between stage 1 and stage 2 
second do the test

'''      

