# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 23:34:16 2018

@author: mgxgl
generate the data

"""


import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))

lib_path= os.path.dirname(PATH) + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Simu/'

import pickle as pk
from simu import Simu
import numpy as np
from scipy import stats

Simu_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.15, 
        "priv_var":0.1,
        "epsilon_var":0.1,
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
            simu_data.append(SIMU.Data_simu_info(n,T,T_end,info_mode,flag_mode))
            
            
            

    return simu_data




if __name__ == '__main__':
    
    start_n=3
    end_n=7
    T=100
    T_end=100
    
    Rng_seed=123
    
    mode_flag=1 # 1 -> run the simulation ; 0 -> read the data
    
    
    
    '''
    the case for uninformed 
    
    '''
    if mode_flag ==1:
        info_flag=0
        flag_mode=2
        simu_data_0= Gen_Simu(start_n,end_n,T,T_end,Simu_para_dict,info_flag,flag_mode)
        with open( data_path + "simu_data_uninfo.pkl", "wb") as f : 
            pk.dump(simu_data_0, f)
    else:
    # load the uninformed case 
        with open( data_path + "simu_data_uninfo.pkl", "rb") as f :
            simu_data_0=pk.load( f)
    #    
    '''
    the case for informed
    
    '''
    if mode_flag ==1:
        info_flag=1
        flag_mode=2
        simu_data_1= Gen_Simu(start_n,end_n,T,T_end,Simu_para_dict,info_flag,flag_mode)
        with open( data_path + "simu_data_info.pkl", "wb") as f:
            pk.dump(simu_data_1, f)
    else:
    # load the uninformed case
        with open( data_path + "simu_data_info.pkl", "rb") as f: 
            simu_data_1=pk.load(f)
        
    
    '''
    calculate the moments for 
    1 winning bid 
    2 bidding frequency
    3 bidding distance
    
    '''
    N_chunk=len(simu_data_1)
    
    # check the moments
    cmp_list=['data_win','sec_diff_i1','sec_freq_i1','low_freq_ratio_i','freq_i1']

    for i in range(0,N_chunk):
        temp_sim_0=simu_data_0[i]
        temp_sim_1=simu_data_1[i]
        sim_0_list=[]
        sim_1_list=[]
        print('for N = {} auctions'.format(temp_sim_1.pub_info[6,2]))
        
        for ele in cmp_list:
    
            sim_0_list.append(np.nanmean(temp_sim_0.data_dict[ele]))
            sim_1_list.append(np.nanmean(temp_sim_1.data_dict[ele]))
            
        print('           -: win bid \t sec_diff_mean \t sec_freq \t low_freq_ratio \t freq')
        print('uninformed -:'+' \t '.join(str(round(x,4)) for x in sim_0_list))
        print('  informed -:'+' \t '.join(str(round(x,4)) for x in sim_1_list))
