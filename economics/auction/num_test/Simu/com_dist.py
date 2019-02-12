# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 23:34:16 2018

@author: mgxgl
compare the distribution between informed case and uninformed case
https://seaborn.pydata.org/tutorial/distributions.html
https://python-graph-gallery.com/

next task:

    randomize the number of bidders in each types of auction

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


## generate simulation data for testing 
def Gen_Simu(start_n,end_n,T,T_end,Simu_para_dict,info_mode=0,flag_mode=0,rng_seed=123):
    '''
    start_n : start number of bidders 
    end_n   : end number of bidders 
    T number of auctions
    T_end bidding path length
    info mode whether it is uninformed case or informed case
                    0: uninformed case 
                    1: informed case
    flag_mode whether it is fix reservation or fix the pub-evaulation or randomize everything
                    0: fix the pub 1: fix the reservation 2: randomize everything
    
    '''
  
    # moving the number 
    if info_mode == 0: 
        simu_data=[]
        for n in range(start_n, end_n+1):
            
            SIMU=Simu(rng_seed,Simu_para_dict)
            simu_data.append(SIMU.Data_simu(n,T,T_end,info_mode,flag_mode))
        
        
    else:
        
        simu_data=[]

        for n in range(start_n, end_n+1):
            
            SIMU=Simu(rng_seed,Simu_para_dict)
            simu_data.append(SIMU.Data_simu_info(n,T,T_end,info_mode,flag_mode))
            
            
            

    return simu_data




if __name__ == '__main__':
    
    start_n=2
    end_n=10
    
    
    PATH= 'G:/github/Project/economics/auction/num_test/simu'
    # without the informed bidder 
    with open( data_path + "simu_data_2_uninfo.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( data_path + "simu_data_2_info.pkl", "rb") as f :
        simu_data_1=pk.load( f)


    '''
    calculate the moments for 
    1 winning bid 
    2 bidding frequency
    3 bidding distance
    
    '''
    

    
    N_chunk=len(simu_data_1)
    
    # check the moments
    cmp_list=['data_win','sec_diff_i1','sec_freq_i1','low_freq_ratio_i','freq_i1']

#        
    for i in range(0,N_chunk):
        temp_sim_0=simu_data_0[i][1]
        temp_sim_1=simu_data_1[i][1]
        sim_0_list=[]
        sim_1_list=[]
        if i ==0:
            sim_0_df=temp_sim_0
            sim_1_df=temp_sim_1
        else:
            sim_0_df=sim_0_df.append(temp_sim_0,ignore_index=True)
            sim_1_df=sim_1_df.append(temp_sim_1,ignore_index=True)
        print('for N = {} auctions'.format(i+2))
        
        for ele in cmp_list:
    
            sim_0_list.append(np.nanmean(temp_sim_0[ele]))
            sim_1_list.append(np.nanmean(temp_sim_1[ele]))
            
        print('           -: win bid \t sec_diff_mean \t sec_freq \t low_freq_ratio \t freq')
        print('uninformed -:'+' \t '.join(str(round(x,4)) for x in sim_0_list))
        print('  informed -:'+' \t '.join(str(round(x,4)) for x in sim_1_list))
#        
    tile = sim_0_df['data_win'].quantile(.95)
    sim_0_df=sim_0_df[sim_0_df['data_win']<tile]
    tile = sim_1_df['data_win'].quantile(.95)
    sim_1_df=sim_1_df[sim_1_df['data_win']<tile]


    # get the bidding info 
    for i in range(0,N_chunk):
        temp_sim_0=simu_data_0[i][0]
        temp_sim_1=simu_data_1[i][0]
        sim_0_list=[]
        sim_1_list=[]
        if i ==0:
            sim_00_df=temp_sim_0
            sim_11_df=temp_sim_1
        else:
            sim_00_df=sim_00_df.append(temp_sim_0,ignore_index=True)
            sim_11_df=sim_11_df.append(temp_sim_1,ignore_index=True)
        print('for N = {} auctions'.format(i+2))



        
    '''
    draw the dist for 
    1 winning bid 
    2 bidding distance
    3 bidding frequency
    '''
    # wining bid hist graph
   cmp_list=['data_win','sec_diff_i1','sec_freq_i1','freq_i1']
   
   n_set=1
   cmp_ele=cmp_list[0]
   
   f, axes = plt.subplots(1, 2, figsize=(7, 7), sharex=True)
   
   x=sim_0_df[cmp_ele]
   tail=np.percentile(x,99)
   x=x[x<tail]
   #sns.distplot(x, hist=False, rug=True,ax=axes[ 0])
   sns.distplot(x, bins=20, kde=False,ax=axes[0])
   axes[0].set_title("uninformed")
   axes[0].set_ylabel('density')
   
   y=sim_1_df[cmp_ele]
   tail=np.percentile(y,99)
   y=y[y<tail]
   #sns.distplot(y, hist=False, rug=True,ax=axes[1])
   sns.distplot(y, bins=20, kde=False,ax=axes[1])
   axes[1].set_title("informed")
   plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.2,left=0.05, right=1.2)
   
   plt.show()
    
    

    '''
    # fix the number of bidder : 
    # winning bid
    '''

    # sim_0_df.loc[sim_0_df['num_i']==4,'data_win']
    xx1 = np.sort(sim_0_df['data_win'])
    xx1 =xx1.astype(float) 
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(sim_1_df['data_win'])
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
    df_result0['eff_rate']=df_result['count_right']/df_result['count_total']
    
    # the informed case : 
    sim_11_df['effiency']=sim_11_df['signal_max_ID']-sim_11_df['winning_ID']
    sim_11_df = sim_11_df[sim_11_df['real_num_bidder']>1]
    df_11_group=sim_11_df.groupby("real_num_bidder")
    df1=df_11_group.effiency.count().reset_index(name='count_total')
    # get the correct part 
    df2=df_11_group.effiency.apply(lambda x: (x==0).sum()).reset_index(name='count_right')
    
    df_result1=pd.merge(df1,df2,on="real_num_bidder")
    df_result1['eff_rate']=df_result['count_right']/df_result['count_total']




    # third winning bid
    xx1 = np.sort(sim_0_df['third_win_i'])
    xx1 =xx1.astype(float) 
    xx1 = xx1[~np.isnan(xx1)]
    density1 = ss.kde.gaussian_kde(xx1)
    xx2 = np.sort(sim_1_df['third_win_i'])
    xx2 = xx2[~np.isnan(xx2)]
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




    '''
    bid frequency
    '''
    N_chunk=len(simu_data_1)
    
    xx1 = np.sort(sim_0_df['freq_i1'])
    density1 = stats.kde.gaussian_kde(xx1)
    xx2 = np.sort(sim_1_df['freq_i1'])
    density2 = stats.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0, 25, 1)
    x2 = np.arange(0, 25, 1)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("bidding times")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of bidding frequency")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)


    '''
    winning bid spread
    '''
    N_chunk=len(simu_data_1)
    big_win_v0=np.array([])
    big_win_v1=np.array([])
    for i in range(0,N_chunk):
        big_win_v0=np.append(big_win_v0,simu_data_0[i].data_win)
        big_win_v1=np.append(big_win_v1,simu_data_1[i].data_win)
        
        
    
    xx1 = np.sort(big_win_v0)
    density1 = stats.kde.gaussian_kde(xx1)
    xx2 = np.sort(big_win_v1)
    density2 = stats.kde.gaussian_kde(xx2)
    
    x1 = np.arange(0.9, 1.4, 0.001)
    x2 = np.arange(0.9, 1.4, 0.001)
    
    _ = plt.plot(x1,density1(x1),label = "without informed bidder")
    _ = plt.plot(x2,density2(x2),label = "with informed bidder")
    _ = plt.xlabel("winning price / reserve price")
    _ = plt.ylabel("Density")
    _ = plt.title("Simulated Distribution of Winning Bid")
    _ = plt.margins(0.02)
    _ = plt.legend(loc='upper right')
    _ = plt.grid(True)    
