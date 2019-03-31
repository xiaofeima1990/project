# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:37:44 2019

@author: xiaofeima

data statistics graph (general)
Here I only focus on the first time auction

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
path = "E:/Dropbox/academic/ideas/IO field/justice auction/code4/analysis/"
store_path="E:/auction/"


# get whole data to analysis
df_1 = pd.read_csv(path+"sample_raw1_df.csv",sep="\t")

# data clean
necessary_col=['index','num_bidder','n_register','priority_people','reserve_price','win_bid','evaluation_price']

# exclude the extreme value
tail1=df_1['num_bidder'].quantile(.95)

df_1_c=df_1.loc[df_1['num_bidder']<tail1,]
df_1_c=df_1_c.loc[df_1['num_bidder']>0,]



# ----------------------------------------------------------------
# draw the Emprical CDF of the number 
# ----------------------------------------------------------------
xx = np.sort(df_1_c['num_bidder'])
yy = np.arange(1,len(xx)+1)/len(xx)
num_bins = 25
counts, bin_edges = np.histogram (df_1_c['num_bidder'], bins=num_bins, normed=True)
cdf = np.cumsum (counts)
_ = plt.plot (bin_edges[1:], cdf/cdf[-1])
_ = plt.plot(xx,yy,marker="_", linestyle = "none")
_ = plt.xlabel("number of bidder")
_ = plt.ylabel("Empirical CDF")  
_ = plt.title("First Time Auction")  
plt.margins(0.02)
plt.annotate('nearly 80% of \n first time auctions \n have less than \n 11 bidders', xy=(9, 0.75), xytext=(11, 0.4),
             arrowprops=dict(facecolor='black', shrink=0.05),
             )
plt.grid(True)


'''
num of successful auction

'''

df_1_c=df_1[df_1['status']=='done']

print("total auctions in xuzhou first time auction: ",len(df_1))
print("total auctions in xuzhou first time auction: ",len(df_1_c))



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

df_1_c=df_1[df_1['status']=='done']
df_1_c['p_res_eva']=df_1_c['reserve_price']/df_1_c['evaluation_price']

df_1_c['resev_proxy'] = (df_1_c['win_bid']-df_1_c['reserve_price'])/df_1_c['reserve_price']
df_1_c.dropna(subset=['p_res_eva','resev_proxy'],inplace=True)

tail1=df_1_c['resev_proxy'].quantile(.99) 
df_1_done=df_1_c.loc[df_1_c['resev_proxy']<tail1,['p_res_eva','resev_proxy']+necessary_col]

tail1=df_1_done['num_bidder'].quantile(.95) 
df_1_done=df_1_done.loc[df_1_done['num_bidder']<tail1,]

tail1=df_1_done['p_res_eva'].quantile(.99) 
df_1_done=df_1_done.loc[df_1_done['p_res_eva']<tail1,]

# first time auction at least larger than 0.7
df_1_done=df_1_done.loc[df_1_done['p_res_eva']>0.7,]
df_1_done=df_1_done.loc[df_1_done['p_res_eva']<=1, ]

plt.scatter(x=df_1_done["num_bidder"], y=df_1_done['resev_proxy'],
            #s=df_1_done['delay_count'], 
#            c=df_1_done['p_res_eva'],
            alpha=0.5)

plt.xlabel("number of bidder")
plt.ylabel("winning price premium")
plt.title("First Time Auction")
#cax = plt.axes([0.95, 0.1, 0.05, 0.8])
#plt.colorbar(cax =cax )
plt.grid(True)
plt.show()



'''
winning bid distrbution across the item value 
 p_ratio = winning / reserve

draw the scatter historgam
'''

df_1_c['p_ratio']=df_1_c['win_bid']/df_1_c['reserve_price']
df_1_c['p_ratio1']=df_1_c['win_bid']/df_1_c['evaluation_price']

tail1=df_1_c['p_ratio'].quantile(.95) 
df_1_done=df_1_c.loc[df_1_c['p_ratio']<tail1,['p_ratio','p_ratio1']+necessary_col]

tail1=df_1_done['num_bidder'].quantile(.95) 
df_1_done=df_1_done.loc[df_1_done['num_bidder']<tail1,]

tail1=df_1_c['p_ratio1'].quantile(.95) 
df_1_done=df_1_done.loc[df_1_done['p_ratio1']<tail1,]


# scatter hist !
from matplotlib.ticker import NullFormatter
nullfmt = NullFormatter()         # no labels

left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left + width + 0.05

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.25]
rect_histy = [left_h, bottom, 0.25, height]


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
plt.margins(0.05)

lim1=df_1_done['num_bidder'].max()
lim2=df_1_done['p_ratio1'].max()
binwidth1= (lim1/30) 
binwidth2= (lim2/30) 
axScatter.set_xlim((1, lim1))
axScatter.set_ylim((0.4, lim2+0.1))

bin1 = np.arange(1, lim1+binwidth1, binwidth1)
bin2 = np.arange(0, lim2+binwidth2, binwidth2)

axHistx.hist(x, bins=bin1,rwidth=0.8 )
axHistx.margins(0.02)
axHisty.hist(y, bins=bin2, orientation='horizontal',rwidth=0.8)
axHisty.margins(0.02)

axHistx.set_xlim(axScatter.get_xlim())
axHisty.set_ylim(axScatter.get_ylim())
axScatter.set_xlabel("number of bidder")
axScatter.set_ylabel("winning bid over evaluation price")
plt.margins(0.05)
plt.grid(True)
plt.show()
