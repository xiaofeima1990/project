# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 23:34:16 2018

@author: mgxgl
test for the equilibrium price premium 
a la Dionne et al 2009

write a new script for simulation
using the HS system to do the calculation 
simulation steps:
1. use randomized parameter sets to generate bidding 
   outcomes (with informed bidder)
   fix the number of bidders, and do this from 4 to 8 
2. select those data that informed bidders wins， replace the 
   informed bidder with uninformed bidder and run the simulation 
   again
3. calculate the price premium and compare across the number of bidders.
   notice that, I should not restrict the reserve price

"""


import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))

lib_path= os.path.dirname(PATH) + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Simu/'

import pickle as pk
import pandas as pd
from simu import Simu
import numpy as np
from scipy import stats

def Gen_Simu_data1(N,T,Simu_para_dict,info_flag=0,rng_seed=123):
    SIMU=Simu(rng_seed,Simu_para_dict)
    # simu_data=[SIMU.Data_simu(N,T,info_flag) for info_flag in range(0,2)]
    
    [simu_data,simu_mom]=SIMU.Data_premium(N,T,info_flag)
    return [simu_data,simu_mom]

def Gen_Simu_data2(start_n,end_n,T,Simu_para_dict,bidding_mode=0,info_mode=0,simu_df=None,rng_seed=123):
    '''
    start_n : start number of bidders 
    end_n   : end number of bidders 
    T number of auctions
    T_end bidding path length
    info mode whether it is uninformed case or informed case
                    0: uninformed case 
                    1: informed case
    bidding_mode whether it is the inoformed case or uninformed for replication
                    0: informed case
                    1: uninformed case
    
    '''
  
    # moving the number
    simu_data=[]
    for n in range(start_n, end_n+1):
        
        SIMU=Simu(rng_seed,Simu_para_dict,bidding_mode)
        if info_mode==0:   
            SIMU.setup_para(simu_df[n-start_n])
        simu_data.append(SIMU.Data_premium(n,T,info_mode))

    return simu_data



Simu_para_dict={

        "comm_mu":0.07,
        "beta":0.905,
        "epsilon_mu":0,
        "comm_var":0.025,
        "priv_var":0.005,
        "epsilon_var":0.036,
        }


if __name__ == '__main__':
    

    info_flag=1
    n_start = 15
    n_end   = 20

    # stage 1 find the winner of informed bidder
    T=200
    
    Rng_seed=123
    info_flag=1 # has the informed bidder (1) or not (0)

    bidding_mode = 0
    simu_data_1= Gen_Simu_data2(n_start,n_end,T,Simu_para_dict,bidding_mode,info_flag)
    with open( data_path + "simu_data_pre1.pkl", "wb") as f : 
        pk.dump(simu_data_1, f)

    # stage 2 find the winner of uninformed bidder
    # with open( data_path + "simu_data_pre1.pkl", "rb") as f :
    #     simu_data_1=pk.load( f)
    info_flag=0 
    bidding_mode = 0
    Rng_seed=123
    simu_data_0= Gen_Simu_data2(n_start,n_end,T,Simu_para_dict,bidding_mode,info_flag,simu_data_1)
    with open( data_path + "simu_data_pre0.pkl", "wb") as f : 
        pk.dump(simu_data_0, f)
    

    # stage 3 cacluate the premium 
    # merge the data
    N_chunk=len(simu_data_1)
    for i in range(0,N_chunk):
        temp_sim_0=simu_data_0[i]
        temp_sim_1=simu_data_1[i]
        sim_0_list=[]
        sim_1_list=[]
        if i ==0:
            sim_00_df=temp_sim_0
            sim_11_df=temp_sim_1
        else: 
            sim_00_df=sim_00_df.append(temp_sim_0,ignore_index=True)
            sim_11_df=sim_11_df.append(temp_sim_1,ignore_index=True)
    

    # select the wining bid 
    sim_11_df['info_win']=sim_11_df['info_bidder_ID']-sim_11_df['winning_ID']
    sim_11_df_c=sim_11_df[sim_11_df['info_win']==0]
    sim_00_df_c=sim_00_df[sim_11_df['info_win']==0]

    # claculate the premium
    prem_df = pd.merge(sim_11_df_c,sim_00_df_c,on='ID')
    prem_df['premium']=prem_df['win2_norm_x']-prem_df['win2_norm_y']
    print(prem_df['premium'].mean())
    prem_df.loc[prem_df['real_num_x']==6,'premium'].mean()