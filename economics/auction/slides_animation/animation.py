# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 23:18:42 2018

@author: mgxgl
this slides is used for making animation 

for eg 

I think I use plt directly

"""


'''
example for seaborn scatter
'''
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

def make_colormap(seq):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}
    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])
    return mcolors.LinearSegmentedColormap('CustomMap', cdict)

data_df=pd.read_csv("demo_data.csv",sep='\t')


c = mcolors.ColorConverter().to_rgb
rvb = make_colormap(
    [c('orange'),0.25, c('aqua'), 0.5, c('red'), 0.75, c('blue')])
legend_elements = [
                    Line2D([0], [0], marker='o', color='orange',alpha=0.5, label='bidder 1',
                      markerfacecolor='orange', markersize=10),
                    Line2D([0], [0], marker='o', color='aqua',alpha=0.5, label='bidder 2',
                      markerfacecolor='aqua', markersize=10),
                    Line2D([0], [0], marker='o', color='red',alpha=0.5, label='bidder 3',
                      markerfacecolor='red', markersize=10),
                    Line2D([0], [0], marker='o', color='blue',alpha=0.5, label='bidder 4',
                      markerfacecolor='blue', markersize=10)]

my_dpi=150
fig_size_w=6.5
fig_size_h=4

# figure 0
fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
plt.xlim(0, 18)
plt.ylim(1000, 3200)
text_content="A Typical English Auction with 4 Bidders\nreserve price: 1000 \nminimum increment: 100\na bidder forms evaluation: $x_i$"

# these are matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
plt.text(1.5,2250,text_content,ha="left", va="center",fontsize=14,bbox=props)

filename='step'+str(1)+'.png'
plt.savefig(filename, dpi=my_dpi)


# figure 1
fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
plt.xlim(0, 18)
plt.ylim(1000, 3200)
#x1=np.linspace(0,18,19)
#y1=np.ones(19)*1650

plt.plot( 'bid_path', 'bidder_1_ex', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1")
plt.plot( 'bid_path', 'bidder_2_ex', data=data_df, marker='', color='aqua',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2")
plt.plot( 'bid_path', 'bidder_3_ex', data=data_df, marker='', color='red',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 3")
plt.plot( 'bid_path', 'bidder_4_ex', data=data_df, marker='', color='blue',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 4")
plt.legend(loc='upper left')
#plt.legend(legend_elements,loc='upper left')

filename='step'+str(2)+'.png'
plt.savefig(filename, dpi=my_dpi)

x1=np.array(data_df['bid_path'][1:])
y1=np.array(data_df['bid_path'][1:])

new_df=data_df.iloc[1:-2,]
new_df['bidder']=pd.Categorical(new_df['bidder'])



for i in range(1,15+1):
    fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
    plt.plot( new_df['bid_path'][:i],new_df['bid_price'][:i], marker='', color='lightblue', linewidth=1.5,zorder=1)
    plt.scatter(new_df['bid_path'][:i],new_df['bid_price'][:i] , s=100, c=new_df['bidder'].cat.codes[:i],cmap=rvb, alpha=0.5, edgecolors="white", linewidth=2,zorder=2)
    if i >= 6:
        plt.plot( 'bid_path', 'bidder_1_ex', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
    
    if i >= 10:
        plt.plot( 'bid_path', 'bidder_1_ex', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_2_ex', data=data_df, marker='', color='aqua',  alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2 valuation",zorder=1)
    
    if i >= 15:
        plt.plot( 'bid_path', 'bidder_1_ex', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_2_ex', data=data_df, marker='', color='aqua',  alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_3_ex', data=data_df, marker='', color='red',   alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 3 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_4_ex', data=data_df, marker='', color='blue',  alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 4 valuation",zorder=1)
    
    plt.legend(handles=legend_elements, loc='upper left')
    plt.xlim(0, 18)
    plt.ylim(1000, 3200)
    plt.xlabel("bidding period")
    plt.ylabel("bidding price")
    
    filename='step'+str(i+2)+'.png'
    plt.savefig(filename, dpi=my_dpi)
    plt.gca()



'''
-------------------------------------------------------------------------------
button auction
-------------------------------------------------------------------------------
'''


my_dpi=150
fig_size_w=6.5
fig_size_h=4

data_df=pd.read_csv("demo_data_button.csv",sep=r',')
new_df=data_df.iloc[1:,]



fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
plt.xlim(0, 22)
plt.xticks(range(0,22+1,5))
plt.ylim(1000, 3200)
text_content='''
Button Auction\n
every bidder acts as press a button\n
bidding price rises continuously\n
anyone who releases the button will quit forever\n'''

# these are matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
plt.text(0.75,2250,text_content,ha="left", va="center",fontsize=14,bbox=props)

filename='step'+str(0)+'.png'
plt.savefig(filename, dpi=my_dpi)

# figure 1
fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
plt.xlim(0, 22)
plt.xticks(range(0,22+1,5))
plt.ylim(1000, 3200)
#x1=np.linspace(0,18,19)
#y1=np.ones(19)*1650

plt.plot( 'bid_path', 'bidder_1_1', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1")
plt.plot( 'bid_path', 'bidder_2_1', data=data_df, marker='', color='aqua',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2")
plt.plot( 'bid_path', 'bidder_3_1', data=data_df, marker='', color='red',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 3")
plt.plot( 'bid_path', 'bidder_4_1', data=data_df, marker='', color='blue',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 4")
plt.legend(loc='upper left')

filename='step'+str(1)+'.png'
plt.savefig(filename, dpi=my_dpi)


c = mcolors.ColorConverter().to_rgb
rvb4 = make_colormap(
    [c('orange'),0.25, c('aqua'), 0.5, c('red'), 0.75, c('blue')])
rvb3 = make_colormap(
    [c('orange'),0.33, c('aqua'), 0.66, c('red')])
rvb2 = make_colormap(
    [c('orange'),0.5, c('aqua')])



legend_elements = [
                    Line2D([0], [0], marker='o', color='orange',alpha=0.5, label='bidder 1',
                      markerfacecolor='orange', markersize=10),
                    Line2D([0], [0], marker='o', color='aqua',alpha=0.5, label='bidder 2',
                      markerfacecolor='aqua', markersize=10),
                    Line2D([0], [0], marker='o', color='red',alpha=0.5, label='bidder 3',
                      markerfacecolor='red', markersize=10),
                    Line2D([0], [0], marker='o', color='blue',alpha=0.5, label='bidder 4',
                      markerfacecolor='blue', markersize=10)]



round_list=[7,14,19,21]

sca_x=new_df.loc[new_df['bidder']!=-1,'bid_path']
sca_y=new_df.loc[new_df['bidder']!=-1,'dropout']
sca_z=new_df.loc[new_df['bidder']!=-1,'bidder']
sca_df=new_df.loc[new_df['bidder']!=-1,['bid_path','dropout','bidder']]

sca_df['bidder']=pd.Categorical(sca_df['bidder'])
count=1

for i in round_list:
    fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
    # draw the bidding path
    plt.plot( new_df['bid_path'][:i],new_df['bid_price'][:i], marker='', color='lightblue', linewidth=1.5,zorder=2)
    # draw each bidder's dropout path
#    plt.plot( 'bid_path', 'bidder_1_1', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1")
#    plt.plot( 'bid_path', 'bidder_2_1', data=data_df, marker='', color='aqua',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2")
#    plt.plot( 'bid_path', 'bidder_3_1', data=data_df, marker='', color='red',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 3")
#    plt.plot( 'bid_path', 'bidder_4_1', data=data_df, marker='', color='blue',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 4")
#    
    if count <= 2:
        rvb=rvb2
    elif count ==3:
        rvb=rvb3
    else:
        rvb=rvb4
        
        
    plt.scatter(sca_df['bid_path'][:count],sca_df['dropout'][:count] , s=100, c=sca_df['bidder'].cat.codes[:count],cmap=rvb, alpha=0.5, edgecolors="white", linewidth=2,zorder=3)
    
    
    # draw each bidder's dropout path
    plt.plot( 'bid_path', 'bidder_1_ex', data=new_df[:i], marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
    plt.plot( 'bid_path', 'bidder_2_ex', data=new_df[:i], marker='', color='aqua',  alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2 valuation",zorder=1)
    plt.plot( 'bid_path', 'bidder_3_ex', data=new_df[:i], marker='', color='red',   alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 3 valuation",zorder=1)
    plt.plot( 'bid_path', 'bidder_4_ex', data=new_df[:i], marker='', color='blue',  alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 4 valuation",zorder=1)
    
    
    plt.legend(handles=legend_elements, loc='upper left')
    plt.xlim(0, 22)
    plt.xticks(range(0,22+1,5))
    plt.ylim(1000, 3200)
    plt.xlabel("bidding period")
    plt.ylabel("bidding price")
    
    filename='step'+str(count)+'.png'
    plt.savefig(filename, dpi=my_dpi)
    count=1+count



'''
-------------------------------------------------------------------------------
english auction with updating process
-------------------------------------------------------------------------------

'''




data_df=pd.read_csv("demo_data_update.csv",sep=',')


c = mcolors.ColorConverter().to_rgb
rvb = make_colormap(
    [c('orange'),0.25, c('aqua'), 0.5, c('red'), 0.75, c('blue')])
legend_elements = [
                    Line2D([0], [0], marker='o', color='orange',alpha=0.5, label='bidder 1',
                      markerfacecolor='orange', markersize=10),
                    Line2D([0], [0], marker='o', color='aqua',alpha=0.5, label='bidder 2',
                      markerfacecolor='aqua', markersize=10),
                    Line2D([0], [0], marker='o', color='red',alpha=0.5, label='bidder 3',
                      markerfacecolor='red', markersize=10),
                    Line2D([0], [0], marker='o', color='blue',alpha=0.5, label='bidder 4',
                      markerfacecolor='blue', markersize=10)]

my_dpi=150
fig_size_w=6.5
fig_size_h=4

# figure 0
fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
plt.xlim(0, 18)
plt.xticks(range(0,18+1,5))
plt.ylim(1000, 3400)
text_content='''
A Common Value English Auction with 4 Bidders\n
Bidders will update their expected valuation
based on past bidding history.
'''
# these are matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
plt.text(0.5,2300,text_content,ha="left", va="center",fontsize=14,bbox=props)

filename='step'+str(0)+'.png'
plt.savefig(filename, dpi=my_dpi)


# figure 1
fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
plt.xlim(0, 18)
plt.xticks(range(0,18+1,5))
plt.ylim(1000, 3400)
#x1=np.linspace(0,18,19)
#y1=np.ones(19)*1650

plt.plot( 'bid_path', 'bidder_1_1', data=data_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1")
plt.plot( 'bid_path', 'bidder_2_2', data=data_df, marker='', color='aqua',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 2")
plt.plot( 'bid_path', 'bidder_3_3', data=data_df, marker='', color='red',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 3")
plt.plot( 'bid_path', 'bidder_4_4', data=data_df, marker='', color='blue',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 4")
plt.legend(loc='upper left')
#plt.legend(legend_elements,loc='upper left')

filename='step'+str(1)+'.png'
plt.savefig(filename, dpi=my_dpi)



# main part
new_df=data_df.iloc[1:-1,]
new_df['bidder']=pd.Categorical(new_df['bidder'])



for i in range(4,17+1):
    fig = plt.figure(figsize=(fig_size_w, fig_size_h), dpi=my_dpi)
    plt.plot( new_df['bid_path'][:i],new_df['bid_price'][:i], marker='', color='lightblue', linewidth=2,zorder=1)
    
    plt.scatter(new_df['bid_path'][:i],new_df['bid_price'][:i] , s=100, c=new_df['bidder'].cat.codes[:i],cmap=rvb, alpha=0.5, edgecolors="white", linewidth=2,zorder=2)
    
    if i >= 4:
        plt.plot( 'bid_path', 'bidder_1_1', data=data_df, marker='', color='orange',alpha=0.25, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
        
        if i ==5:
            text_content='Based on past 3 period \nbidding price history,\nbidder 1 will update to \n$E[V|X_1,X_2,X_3] = 1700$.'
            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle='round', alpha=0.5)
            plt.annotate(text_content, xy=(5,1700), xytext=(6, 2000),fontsize=11,
             arrowprops=dict(facecolor='black', shrink=0.06),
             )
        plt.plot( 'bid_path', 'bidder_1_ex', data=new_df[:i], marker='', color='orange',alpha=0.75, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
        
    
    if i >= 6:
#        plt.plot( 'bid_path', 'bidder_1_ex', data=new_df, marker='', color='orange',alpha=0.5, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_2_ex', data=new_df[:i], marker='', color='aqua',  alpha=0.75, linewidth=2, linestyle='dashed', label="bidder 2 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_3_ex', data=new_df[:i], marker='', color='red',   alpha=0.75, linewidth=2, linestyle='dashed', label="bidder 3 valuation",zorder=1)
        plt.plot( 'bid_path', 'bidder_4_ex', data=new_df[:i], marker='', color='blue',  alpha=0.75, linewidth=2, linestyle='dashed', label="bidder 4 valuation",zorder=1)
        
        if i == 8:
            text_content='after updating, bidder 1\ncan now bid at 1700!'
            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle='round', alpha=0.5)
            plt.annotate(text_content, xy=(8,1700), xytext=(8, 2300),fontsize=11,
             arrowprops=dict(facecolor='black', shrink=0.06),
             )
        plt.plot( 'bid_path', 'bidder_1_ex', data=new_df[:i], marker='', color='orange',alpha=0.75, linewidth=2, linestyle='dashed', label="bidder 1 valuation",zorder=1)
        
        
        if i == 13:
            text_content='At higher price,some bidders will\nstop updating bidding price.\nThe updating process will be slower'
            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle='round', alpha=0.5)
            plt.annotate(text_content, xy=(11,3120), xytext=(7, 2400),fontsize=11,
             arrowprops=dict(facecolor='black', shrink=0.06),
             )
            
        
    plt.legend(handles=legend_elements, loc='upper left')
    plt.xlim(0, 18)
    plt.xticks(range(0,18+1,5))
    plt.ylim(1000, 3400)
    plt.xlabel("bidding period")
    plt.ylabel("bidding price")
    
    filename='step'+str(i-2)+'.png'
    plt.savefig(filename, dpi=my_dpi)
    plt.gca()

