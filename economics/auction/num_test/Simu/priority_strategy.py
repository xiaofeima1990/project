# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:24:24 2019

@author: mgxgl
this is used for simulating the priority bidder's strategic behavior 

"""

import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))
print(PATH)
lib_path= os.path.dirname(PATH) + '/lib/'
# lib_path= PATH + '/lib/'
print(lib_path)
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Simu/'


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pickle as pk
# from simu import Simu
import numpy as np
from scipy import stats
import scipy.stats as ss



if __name__ == '__main__':
    
    start_n=2
    end_n=10
    
    
    # ----------------------------------------------------------
    ## simple comparison for normal bidding 
    # ----------------------------------------------------------
    PATH= 'G:/github/project/economics/auction/num_test/data/Simu/'
    
    with open( PATH + "simu_data_2_uninfo-0.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( PATH + "simu_data_2_info-0.pkl", "rb") as f :
        simu_data_1=pk.load( f)
        
    N_chunk=len(simu_data_0)
    n_start=0
    for i in range(n_start,N_chunk):
        temp_sim_0=simu_data_0[i][1]
        sim_0_list=[]
        if i ==n_start:
            sim_0_df=temp_sim_0
        else:
            sim_0_df=sim_0_df.append(temp_sim_0,ignore_index=True)
        print('for N = {} auctions'.format(i+2))

    N_chunk=len(simu_data_1)
    n_start=0
    # for informed bidder start from n=3 at least 
    for i in range(n_start,N_chunk):
        temp_sim_1=simu_data_1[i][1]
        sim_1_list=[]
        if i ==n_start:
            sim_1_df=temp_sim_1
        else:
            sim_1_df=sim_1_df.append(temp_sim_1,ignore_index=True)
        print('for N = {} auctions'.format(i+2))




    xx1 = np.sort(sim_0_df['data_win'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(sim_1_df['data_win'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    x1 = np.arange(0.7, 2, 0.001)
    x2 = np.arange(0.7, 2, 0.001)

    _ = plt.plot(x1,density1(x1),label = "without informed")
    _ = plt.plot(x2,density2(x2),label = "with informed - normal")

    _ = plt.xlabel("winning price / reserve price")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of Winning Bid")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    


    # ----------------------------------------------------------
    # comparison for all the strategies 
    # ----------------------------------------------------------
    
    PATH= 'E:/github/Project/economics/auction/num_test/simu'
    # without the informed bidder 
    with open( data_path + "simu_data_2_uninfo-0.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( data_path + "simu_data_2_info-0.pkl", "rb") as f :
        simu_data_1=pk.load( f)
    # prepare for comparison
    with open( data_path + "simu_data_2_info-1.pkl", "rb") as f :
        simu_data_11=pk.load( f)
    with open( data_path + "simu_data_2_info-2.pkl", "rb") as f :
        simu_data_12=pk.load( f)



    
    N_chunk=len(simu_data_1)
    
    # check the moments
    cmp_list=['data_win','sec_diff_i1','sec_freq_i1','low_freq_ratio_i','freq_i1']

#        


    for i in range(0,N_chunk):
        temp_sim_0=simu_data_0[i][0]
        temp_sim_10=simu_data_1[i][0]
        temp_sim_11=simu_data_11[i][0]
        temp_sim_12=simu_data_12[i][0]
        sim_0_list=[]
        sim_10_list=[]
        sim_11_list=[]
        sim_12_list=[]
        if i ==0:
            sim_00_df=temp_sim_0
            sim_10_df=temp_sim_10
            sim_11_df=temp_sim_11
            sim_12_df=temp_sim_12
        else:
            sim_00_df=sim_0_df.append(temp_sim_0,ignore_index=True)
            sim_10_df=sim_10_df.append(temp_sim_10,ignore_index=True)
            sim_11_df=sim_11_df.append(temp_sim_11,ignore_index=True)
            sim_12_df=sim_12_df.append(temp_sim_12,ignore_index=True)
        print('for N = {} auctions'.format(i+2))


    tile = sim_0_df['data_win'].quantile(.95)
    sim_0_df=sim_0_df[sim_0_df['data_win']<tile]
    tile = sim_1_df['data_win'].quantile(.95)
    sim_1_df=sim_1_df[sim_1_df['data_win']<tile]



    '''
    graph for wining bid 
    '''
    
    xx1 = np.sort(sim_0_df['data_win'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(sim_10_df['data_win'])
    xx2 =xx2.astype(float)
    density2 = ss.kde.gaussian_kde(xx2)
    xx3 = np.sort(sim_11_df['data_win'])
    xx3 =xx3.astype(float)
    density3 = ss.kde.gaussian_kde(xx3)
    xx4 = np.sort(sim_12_df['data_win'])
    xx4 =xx4.astype(float)
    density4 = ss.kde.gaussian_kde(xx4)

    
    x1 = np.arange(0.7, 2, 0.001)
    x2 = np.arange(0.7, 2, 0.001)
    x3 = np.arange(0.7, 2, 0.001)
    x4 = np.arange(0.7, 2, 0.001)
    
    _ = plt.plot(x1,density1(x1),label = "without informed")
    _ = plt.plot(x2,density2(x2),label = "with informed - normal")
    _ = plt.plot(x3,density3(x3),label = "with informed - active")
    _ = plt.plot(x4,density4(x4),label = "with informed - not show")
    _ = plt.xlabel("winning price / reserve price")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of Winning Bid")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    



    '''
    efficiency 
    '''
    
    '''
    # get the bidding efficiency
    # signal_max_ID winning_ID
    '''

    
    # the uninformed case : 
    sim_00_df['effiency']=sim_00_df['signal_max_ID']-sim_00_df['winning_ID']
    df_00_group=sim_00_df.groupby("real_num_bidder")
    df1=df_00_group.effiency.count().reset_index(name='count_total')
    # get the correct part 
    df2=df_00_group.effiency.apply(lambda x: (x==0).sum()).reset_index(name='count_right')
    
    df_result0=pd.merge(df1,df2,on="real_num_bidder")
    df_result0['eff_rate']=df_result0['count_right']/df_result0['count_total']
    
    # the informed case normal :
    sim_10_df['effiency']=sim_10_df['signal_max_ID']-sim_10_df['winning_ID']
    sim_10_df = sim_10_df[sim_10_df['real_num_bidder']>1]
    df_10_group=sim_10_df.groupby("real_num_bidder")
    df1=df_10_group.effiency.count().reset_index(name='count_total')
    df2=df_10_group.effiency.apply(lambda x: (x==0).sum()).reset_index(name='count_right')
    df_result10=pd.merge(df1,df2,on="real_num_bidder")
    df_result10['eff_rate']=df_result10['count_right']/df_result10['count_total']
    
    # the informed case active : 
    sim_11_df['effiency']=sim_11_df['signal_max_ID']-sim_11_df['winning_ID']
    sim_11_df = sim_11_df[sim_11_df['real_num_bidder']>1]
    df_11_group=sim_11_df.groupby("real_num_bidder")
    df1=df_11_group.effiency.count().reset_index(name='count_total')
    df2=df_11_group.effiency.apply(lambda x: (x==0).sum()).reset_index(name='count_right')
    df_result11=pd.merge(df1,df2,on="real_num_bidder")
    df_result11['eff_rate']=df_result11['count_right']/df_result11['count_total']
    
    # the informed case scilent : 
    sim_12_df['effiency']=sim_12_df['signal_max_ID']-sim_12_df['winning_ID']
    sim_12_df = sim_12_df[sim_12_df['real_num_bidder']>1]
    df_12_group=sim_12_df.groupby("real_num_bidder")
    df1=df_12_group.effiency.count().reset_index(name='count_total')
    df2=df_12_group.effiency.apply(lambda x: (x==0).sum()).reset_index(name='count_right')
    df_result12=pd.merge(df1,df2,on="real_num_bidder")
    df_result12['eff_rate']=df_result12['count_right']/df_result12['count_total']


