# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 17:12:27 2019

@author: xiaofeima
this is used for New Simulation Test



"""
import matplotlib.pyplot as plt
import pickle as pk
import os,sys
sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))
lib_path= os.path.dirname(PATH) + '/lib/'
# lib_path= PATH + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Simu/'
from Update_rule import Update_rule
from est import Est
from ENV import ENV
import numpy as np
import pandas as pd
import random
import scipy.stats as ss

if __name__ == '__main__':
    # read the data 
    PATH= 'E:/github/Project/economics/auction/num_test/simu'
    # without the informed bidder 
    with open( data_path + "simu_data_10-rand.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( data_path + "simu_data_11-rand.pkl", "rb") as f :
        simu_data_1=pk.load( f)
        
    
    # subsampling https://stackoverflow.com/questions/18713929/subsample-pandas-dataframe
    # df.sample
    # sample(self, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None) method of pandas.core.frame.DataFrame instance
    # Returns a random sample of items from an axis of object.



    # clean the data 
    df_0=simu_data_0[0]
    
    temp_df=simu_data_0[1]
    temp_df=temp_df.reset_index()
    temp_df.rename(columns={'index':'ID'},inplace= True)
    
    df_0=df_0.merge(temp_df,on='ID',how='inner')
    
    
    df_1=simu_data_1[0]
    temp_df=simu_data_1[1]
    temp_df=temp_df.reset_index()
    temp_df.rename(columns={'index':'ID'},inplace= True)
    
    df_1=df_1.merge(temp_df,on='ID',how='inner')


    # clean data
    tile = df_0['data_win'].quantile(.95)
    df_0_c=df_0[df_0['data_win']<tile]
    tile = df_1['data_win'].quantile(.95)
    df_1_c=df_1[df_1['data_win']<tile]


    # -------------------------------------------------------------
    # 1: used for calculating equilibrium bidding premium a la Dionne et al 2009
    # 1.1 all the prices 
    #     pi(i,k,j) = b^1(i,k,j) - b^0(i,k,j) 
    #     for angent i, simulated replication j and bidding round k 
    # 1.2 winnig bid
    #     pi(i=2,k=N-1,j|I=1,k=N,j) = b^1(i,k,j|I=1,k=N,j) - b^0(i=2,k=N-1,j) 
    # -------------------------------------------------------------

    # 1.1 for each rank order of the posting bid, calculate the 25%, 50% 75% percentile bid premium for informed and uninformed
ii=8
while ii>=2:

    df_1_temp=df_1_c[df_1_c['num_i']==ii]
    df_1_temp.reset_index(drop=True,inplace=True)
    equ_price_1=np.zeros([df_1_temp.shape[0],8])
    # record the rank order of the informed guy 
    inform_bid=np.zeros([df_1_temp.shape[0],2])
    

    for index, row in df_1_temp.iterrows():
        # 
        # rank order of the posting price
        rank_index=ss.rankdata(row['bidder_state'],method='min')
        # informed id positition and price 
        inform_bid[index,0] = rank_index[row['info_bidder_ID']] - 1
        inform_bid[index,1] = row['price_norm'][row['bidder_state'][row['info_bidder_ID']]]
        
        order_index=np.argsort(rank_index)[::-1]
        # get the ordered posting price 
        equ_price_1[index,]=row['price_norm'][row['bidder_state'][order_index]]
        
    

    df_0_temp=df_0_c.loc[df_0_c['num_i']==ii,]
    df_0_temp.reset_index(drop=True,inplace=True)
    equ_price_0=np.zeros([df_0_temp.shape[0],8])
    # record the rank order of the informed guy 

    for index, row in df_0_temp.iterrows():
        if index <1057:
            # rank order of the posting price
            rank_index=ss.rankdata(row['bidder_state'],method='min')
            
            order_index=np.argsort(rank_index)[::-1]
            # get the ordered posting price 
            equ_price_0[index,]=row['price_norm'][row['bidder_state'][order_index]]
            


    length=min(df_1_temp.shape[0],df_0_temp.shape[0])
    
    equ_price_1=equ_price_1[:length,]
    equ_price_0=equ_price_0[:length,]
    # shit no use 
    diff = equ_price_1 - equ_price_0
    per_50 =  np.percentile(diff, 50, axis=0)
    mean_dif = np.mean(diff, axis=0)
    print(per_50)
    ii -=1 
    
    # -------------------------------------------------------------
    # 2: used for generating the value distribution under informed and 
    #    uninformed case. 
    # 2.1 fixed # of bidders: winning bid, bid freqency, 
	# 2.2 use possion process to randomize # of bidders. 
	# -------------------------------------------------------------
    PATH= 'E:/github/Project/economics/auction/num_test/data/Simu/'
    # without the informed bidder 
    with open( PATH + "simu_data_2_uninfo.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( PATH + "simu_data_2_info.pkl", "rb") as f :
        simu_data_1=pk.load( f)


    # clean the data 
    df_0=simu_data_0[0]
    
    temp_df=simu_data_0[1]
    temp_df=temp_df.reset_index()
    temp_df.rename(columns={'index':'ID'},inplace= True)
    
    df_0=df_0.merge(temp_df,on='ID',how='inner')
    
    
    df_1=simu_data_1[0]
    temp_df=simu_data_1[1]
    temp_df=temp_df.reset_index()
    temp_df.rename(columns={'index':'ID'},inplace= True)
    
    df_1=df_1.merge(temp_df,on='ID',how='inner')


    # clean data
    tile = df_0['data_win'].quantile(.95)
    df_0_c=df_0[df_0['data_win']<tile]
    tile = df_1['data_win'].quantile(.95)
    df_1_c=df_1[df_1['data_win']<tile]




    # fix the number of bidder : 
    # winning bid 

    xx1 = np.sort(df_0_c['data_win'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(df_1_c['data_win'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0.7, 2, 0.001)
    x2 = np.arange(0.7, 2, 0.001)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("winning price / reserve price")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of Winning Bid")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    



    # -------------------------------------------------------------
    # 3: try to find way to decompose the channels for the learning effect, 
    #    private value, and competitive effect.
    # fix the number of bidders
    # -------------------------------------------------------------
    
    
    # draw general graph for the simulation
    
    # frequency
    xx1 = np.sort(df_0_c['len_act'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(df_1_c['len_act'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0, 40, 1)
    x2 = np.arange(0, 40, 1)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("bidding times")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of bidding frequency")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)



    # wining bid
    xx1 = np.sort(df_0_c['data_win'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(df_1_c['data_win'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0.7, 2, 0.001)
    x2 = np.arange(0.7, 2, 0.001)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("winning price / reserve price")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of Winning Bid")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    


    # third winning price 
    xx1 = np.sort(df_0_c['third_win_i'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(df_1_c['third_win_i'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0.5,2, 0.01)
    x2 = np.arange(0.5,2, 0.01)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel(" normalized bidding price")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of Third Highest Bidding Price")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    




    # distance -> learning effect 

    xx1 = np.sort(df_0_c['sec_diff_i1'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(df_1_c['sec_diff_i1'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0, 35, 1)
    x2 = np.arange(0, 35, 1)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("bid ladder distance")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of bidding distance")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    


    # fix the number of bidders 
    xx1 = np.sort(df_0_c.loc[df_0_c['num_i']==4,'sec_diff_i1'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(df_1_c.loc[df_1_c['num_i']==4,'sec_diff_i1'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0, 35, 1)
    x2 = np.arange(0, 35, 1)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("bid ladder distance")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of bidding distance")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    


