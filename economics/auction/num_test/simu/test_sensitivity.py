# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 15:01:22 2018

@author: xiaofeima

next job: 
    compare the dynamic version of key moments when we change the number of bidders

"""


import matplotlib.pyplot as plt
import pickle as pk
from simu import Simu
from Update_rule import Update_rule
from est import Est
from ENV import ENV
import numpy as np

Simu_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }



## generate simulation data for testing 
def Gen_Simu(N,T,T_end,Simu_para_dict,flag_num,info_mode=0,flag_mode=0,rng_seed=123):
    '''
    N number of register bidders 
    T number of auctions
    T_end bidding path length
    flag_num whether it is fixed N to genertate or starting from 2 to N
                    0: fix the N 1: start from 2 to N
    flag_mode whether it is fix reservation or fix the pub-evaulation or randomize everything
                    0: fix the pub 1: fix the reservation 2: randomize everything
    
    '''
  
    # moving the number 
    if flag_num == 0: 
        SIMU=Simu(rng_seed,Simu_para_dict)
        simu_data=SIMU.Data_simu(N,T,T_end,info_mode,flag_mode)
        
    else:
        
        simu_data=[]

        for n in range(3, N+1):
            
            SIMU=Simu(rng_seed,Simu_para_dict)
            simu_data.append(SIMU.Data_simu(n,T,T_end,flag_mode))
            
            
            

    return simu_data


def SM_compute(simu_data):

    SM_mu={
                'data_win_min'  :np.nanmean(simu_data.data_win),
                'freq_i_mu':     np.nanmean(simu_data.freq_i),
                'freq_dis_i1_mu':np.nanmean(simu_data.freq_dis_i1),
                'freq_dis_i2_mu':np.nanmean(simu_data.freq_dis_i2),
                
                'sec_diff_i1_mu':np.nanmean(simu_data.sec_diff_i1),
                'sec_diff_i2_mu':np.nanmean(simu_data.sec_diff_i2),
                'sec_freq_i1_mu':np.nanmean(simu_data.sec_freq_i1),
                'sec_freq_i2_mu':np.nanmean(simu_data.sec_freq_i2),
                'tot_freq_i_mu' :np.nanmean(simu_data.tot_freq_i),
                'win_rd_price_mu':np.nanmean(simu_data.third_win_i),
                
            
            
            }
    
    SM_std={
                'data_win_std'  :np.nanstd(simu_data.data_win),
                'freq_dis_i1_std':np.nanstd(simu_data.freq_dis_i1),
                'freq_dis_i2_std':np.nanstd(simu_data.freq_dis_i2),
                
                'sec_diff_i1_std':np.nanstd(simu_data.sec_diff_i1),
                'sec_diff_i2_std':np.nanstd(simu_data.sec_diff_i2),
                'sec_freq_i1_std':np.nanstd(simu_data.sec_freq_i1),
                'sec_freq_i2_std':np.nanstd(simu_data.sec_freq_i2),
                'tot_freq_i_std' :np.nanstd(simu_data.tot_freq_i),
                'win_rd_price_std':np.nanstd(simu_data.third_win_i),
                
            
            
            }

    return [SM_mu,SM_std]


if __name__ == '__main__':
    
    ## pre parameter
    N=5
    T=100
    T_end=65
    info_flag=0
    flag_mode=0
    Rng_seed=123
    
    test_para_dict={
    
            "comm_mu":10,
            "priv_mu":1,
            "epsilon_mu":0,
            "comm_var":0.8,
            "priv_var":1.2,
            "epsilon_var":0.8,
            }
    
    flag_num=0
    flag_mode=0
    info_flag=0
    
    tt=[0.8,0.9,1,1.1,1.2,1.3,1.4]
    SM3_v=[]
    SP3_v=[]
    print("# of bidder in this test is " + str(N))
    for ele in tt:
        test_para_dict['epsilon_var']=ele
    
        simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
        [SM3,SP3] = SM_compute(simu_data_test)
        SM3_v.append(SM3)
        SP3_v.append(SP3)
        print("epsilon_var: "+str(test_para_dict["epsilon_var"]))
        print([SM3,SP3])
        
        

# check the difference between different number of bidders
        
    N=4

    
    flag_num=0
    flag_mode=0
    info_flag=0
    
    tt=[0.8,0.9,1,1.1,1.2,1.3,1.4]
    SM3_v=[]
    SP3_v=[]
    print("# of bidder in this test is " + str(N))
    for ele in tt:
        test_para_dict['epsilon_var']=ele
    
        simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
        [SM3,SP3] = SM_compute(simu_data_test)
        SM3_v.append(SM3)
        SP3_v.append(SP3)
        print("epsilon_var: "+str(test_para_dict["epsilon_var"]))
        print([SM3,SP3])
    
    


