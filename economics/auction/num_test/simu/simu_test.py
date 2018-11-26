# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 23:32:31 2018

@author: mgxgl

This is for simulation test: 
    1. generate the simulated data
    2. draw the distribution and moments conditions from the simulated data
    3. test the sensitivity of the parameters
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
#    SM={
#            "data_win_mu":np.nanmean(simu_data.data_win),
#            "freq_dis_i_mu":np.nanmean(simu_data.freq_dis_i),
#            "num_i_mu":np.nanmean(simu_data.num_i),
#            "diff_i_mu":np.nanmean(simu_data.diff_i),
#            "freq_i_mu": np.nanmean(simu_data.freq_i),
#            'diff_pos_i_mu':np.nanmean(simu_data.diff_pos_i),
#            'freq_div_i_mu':np.nanmean(simu_data.freq_div_i),
#            "data_win_std":np.nanstd(simu_data.data_win),
#            "freq_dis_i_std":np.nanstd(simu_data.freq_dis_i),
#            "num_i_std":np.nanstd(simu_data.num_i),
#            "diff_i_std":np.nanstd(simu_data.diff_i),
#            "freq_i_std": np.nanstd(simu_data.freq_i),
#            'diff_pos_i_std':np.nanstd(simu_data.diff_pos_i),
#            'freq_div_i_std':np.nanstd(simu_data.freq_div_i),
#
#            }
    
#    SP={
#            'data_win_25':np.percentile(simu_data.data_win,25),
#            'data_win_50':np.percentile(simu_data.data_win,50),
#            'data_win_75':np.percentile(simu_data.data_win,75),
#            "diff_i_25"  :np.percentile(simu_data.diff_i,25),
#            "diff_i_50"  :np.percentile(simu_data.diff_i,50),
#            "diff_i_75"  :np.percentile(simu_data.diff_i,75),
#            "freq_dis_i_25"  :np.percentile(simu_data.freq_dis_i,25),
#            "freq_dis_i_50"  :np.percentile(simu_data.freq_dis_i,50),
#            "freq_dis_i_75"  :np.percentile(simu_data.freq_dis_i,75),
#            }
#        

    SM_mu={
                'freq_dis_i1_mu':np.nanmean(simu_data.freq_dis_i1),
                'freq_dis_i2_mu':np.nanmean(simu_data.freq_dis_i2),
                
                'sec_diff_i1_mu':np.nanmean(simu_data.sec_diff_i1),
                'sec_diff_i2_mu':np.nanmean(simu_data.sec_diff_i2),
                'sec_freq_i1_mu':np.nanmean(simu_data.sec_freq_i1),
                'sec_freq_i2_mu':np.nanmean(simu_data.sec_freq_i2),
                'tot_freq_i_mu' :np.nanmean(simu_data.tot_freq_i),
                'win_rd_price_mu':np.nanmean(simu_data.win_rd_price),
                
            
            
            }
    
    
        
    SM_std={
                'freq_dis_i1_std':np.nanstd(simu_data.freq_dis_i1),
                'freq_dis_i2_std':np.nanstd(simu_data.freq_dis_i2),
                
                'sec_diff_i1_std':np.nanstd(simu_data.sec_diff_i1),
                'sec_diff_i2_std':np.nanstd(simu_data.sec_diff_i2),
                'sec_freq_i1_std':np.nanstd(simu_data.sec_freq_i1),
                'sec_freq_i2_std':np.nanstd(simu_data.sec_freq_i2),
                'tot_freq_i_std' :np.nanstd(simu_data.tot_freq_i),
                'win_rd_price_std':np.nanstd(simu_data.win_rd_price),
                
            
            
            }        


    return [SM_mu,SM_std]

# load the data
path = "G:\\github\\project\\economics\\auction\\num_test\\"

simu_data = pk.load( open( path+ "simu_data.pkl", "rb"))





'''
testing the parameter sensitivity : 
    given initial paramter space theta_0 and simulate the data 
    calculate the related distribution and moment conditions, percentiles
    
    change one parameter and check the variations of the moment conditions and distributions
    
    


'''

if __name__ == '__main__':
## pre parameter
    N=4
    T=100
    T_end=60
    info_flag=0
    flag_mode=0
    Rng_seed=123



## generate the testing simulation data


    # load the benchmark data 
    simu_data_0=pk.load( open( path+ "simu_data_test0.pkl", "rb"))
    
    [SM0,SP0] = SM_compute(simu_data_0)


## test for the parameter

## variance changes: bigger direction

# change the private var from 1.2 to 1.5
test_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.5,
        "epsilon_var":0.8,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM1,SP1] = SM_compute(simu_data_test)


# change the common var from 0.8 to 1.2 
test_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":1.2,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM2,SP2] = SM_compute(simu_data_test)


# change the epsilon var 
test_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":1.3,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM3,SP3] = SM_compute(simu_data_test)


## variance changes: smaller direction

# change the private var from 1.2 to 1.5
test_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":0.7,
        "epsilon_var":0.8,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM11,SP11] = SM_compute(simu_data_test)


# change the common var from 0.8 to 1.2 
test_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.5,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM21,SP21] = SM_compute(simu_data_test)


# change the epsilon var 
test_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.5,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM31,SP31] = SM_compute(simu_data_test)






# change the private mu
test_para_dict={

        "comm_mu":10,
        "priv_mu":2,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }

flag_num=0
flag_mode=0
info_flag=0

simu_data_test= Gen_Simu(N,T,T_end,test_para_dict,flag_num,0,0)
[SM4,SP4] = SM_compute(simu_data_test)



    
# draw histgram

## number of bidders 

plt.hist(simu_data.num_i, bins='auto') 

## bidd freqency distance
plt.hist(simu_data.freq_i, bins='auto') 

## 
plt.hist(simu_data.diff_i, bins='auto')



