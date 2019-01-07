# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 23:34:16 2018

@author: mgxgl
generate the data

new modification: 
now we have five parameters for value distribution, in the data generation script, our object is to generate the simulated data preparing for the simulation tests.
The general guideness for the data generating process. 
1. randomize the number of bidders at the very beginning
2. of course, we can also do the fixed number of bidders
3. the reservation price and evaluation price
4. most importantly, the bidding ladder!
5. randomize the private signal xi and include the entry threshold
6. bidding path needs to be calculated one by one
----
In the data generating process, we will generate a couple of simulated data set for :
1. equilibrium bidding price comparison (Dionne et al 2009)
2. moment sensitivity test
3. estimation procedure test
4. pi justicification test




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

        "comm_mu":1,
        "priv_mu":0.1,
        "comm_var":0.5,
        "priv_var":0.15,
        "epsilon_var":0.3,
        }



## generate simulation data for testing 
def Gen_Simu_data2(start_n,end_n,T,T_end,Simu_para_dict,info_mode=0,rng_seed=123):
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
            simu_data.append(SIMU.Data_simu(n,T,T_end,info_mode))
        
        
    else:
        
        simu_data=[]

        for n in range(start_n, end_n+1):
            
            SIMU=Simu(rng_seed,Simu_para_dict)
            simu_data.append(SIMU.Data_simu(n,T,info_mode,T_end))
            
            
            

    return simu_data

## generate the simulated data for equilibrium bidding premium
def Gen_Simu_data1(N,T,Simu_para_dict,rng_seed=123):
    SIMU=Simu(rng_seed,Simu_para_dict)
    # simu_data=[SIMU.Data_simu(N,T,info_flag) for info_flag in range(0,2)]
    info_flag=0
    [simu_data,simu_mom]=SIMU.Data_simu(N,T,info_flag)
    return [simu_data,simu_mom]





if __name__ == '__main__':
    

    mode_flag2=0
    mode_flag=1 # 1 -> run the simulation ; 0 -> read the data
    
    '''
    case 1 : fix the number of bidders and calculate the equiblirum bidding premium:
    bid price difference with and without the informed bidder 

    '''
    if mode_flag == 1 :
    ## parameters
        N= 5
        SS= 200
        Rng_seed= 1245
        simu_data_1= Gen_Simu_data1(N,SS,Simu_para_dict,Rng_seed)

        with open( data_path + "simu_data_1.pkl", "wb") as f : 
            pk.dump(simu_data_1, f)

    elif mode_flag==2:
    
    
        '''
        case 2: moment sensitivity test
        1. loop the number of bidders from 2 to 10, and generate the data set
        2. with or without the informed bidders 
        
        '''
        # setup the environment paramers
        start_n=2
        end_n=10
        T=150
        
        Rng_seed=123
        info_flag=0 # has the informed bidder (1) or not (0)
        simu_data_2= Gen_Simu_data2(start_n,end_n,T,Simu_para_dict,info_flag)
        with open( data_path + "simu_data_2_uninfo.pkl", "wb") as f : 
            pk.dump(simu_data_2, f)


        info_flag=1 # has the informed bidder (1) or not (0)
        simu_data_2= Gen_Simu_data2(start_n,end_n,T,Simu_para_dict,info_flag)
        with open( data_path + "simu_data_2_info.pkl", "wb") as f : 
            pk.dump(simu_data_2, f)

    # # load the uninformed case 
    # with open( data_path + "simu_data_uninfo.pkl", "rb") as f :
    #     simu_data_0=pk.load( f)
 
    
    '''
------------------------------------------------------------------------------------
    calculate the moments for 
    1 winning bid 
    2 bidding frequency
    3 bidding distance
------------------------------------------------------------------------------------
    '''

    if mode_flag2==1:
        N_chunk=len(simu_data_1)
        
        # check the moments
        cmp_list=['data_win','sec_diff_i1','sec_freq_i1','low_freq_ratio_i','freq_i1']
        with open( data_path + "simu_data_2_uninfo.pkl", "rb") as f :
            simu_data_21=pk.load( f)
        with open( data_path + "simu_data_2_info.pkl", "rb") as f :
            simu_data_22=pk.load( f)

        for i in range(0,N_chunk):
            temp_sim_0=simu_data_21[i]
            temp_sim_1=simu_data_22[i]
            sim_0_list=[]
            sim_1_list=[]
            print('for N = {} auctions'.format(temp_sim_1.pub_info[6,2]))
            
            for ele in cmp_list:
        
                sim_0_list.append(np.nanmean(temp_sim_0.data_dict[ele]))
                sim_1_list.append(np.nanmean(temp_sim_1.data_dict[ele]))
                
            print('           -: win bid \t sec_diff_mean \t sec_freq \t low_freq_ratio \t freq')
            print('uninformed -:'+' \t '.join(str(round(x,4)) for x in sim_0_list))
            print('  informed -:'+' \t '.join(str(round(x,4)) for x in sim_1_list))
