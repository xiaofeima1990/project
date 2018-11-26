# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 23:34:16 2018

@author: mgxgl
compare the distribution between informed case and uninformed case
https://seaborn.pydata.org/tutorial/distributions.html
https://python-graph-gallery.com/

next task:
    finish the informed bidder simulation 
    randomize the number of bidders in each types of auction

"""


import matplotlib.pyplot as plt
import seaborn as sns


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
            simu_data.append(SIMU.Data_simu(n,T,T_end,info_mode,flag_mode))
            
            
            

    return simu_data




if __name__ == '__main__':
    
    start_n=3
    end_n=5
    T=100
    T_end=65
    
    flag_mode=0
    Rng_seed=123
    

    
    '''
    the case for uninformed 
    
    '''
    
    info_flag=0
    flag_mode=0
    # load the uninformed case 
    path = "G:\\github\\project\\economics\\auction\\num_test\\simu\\"
    simu_data_0=pk.load( open( path+ "simu_data_uninfo.pkl", "rb"))
    
    '''
    the case for informed
    
    '''
    
    info_flag=1
    flag_mode=0
    simu_data_1= Gen_Simu(start_n,end_n,T,T_end,Simu_para_dict,info_flag,flag_mode)
    
    
    '''
    draw the dist for 
    1 winning bid 
    2 bidding frequency
    
    '''
    
    temp_sim_0=simu_data_0[0]
    temp_sim_1=simu_data_1[0]
    
    sns.set(color_codes=True)