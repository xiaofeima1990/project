# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 16:29:31 2018

@author: mgxgl

main test for data estimation 

"""

import os 
import sys


#sys.path.append('/storage/work/g/gum27/system/pkg/')

'''
install the package :
    eg. I am in the work directory and want to install on the pkg 
    pip install --target=system/pkg/ package_name

'''

PATH = os.path.dirname(os.path.realpath(__file__))

lib_path= os.path.dirname(PATH) + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Est/'



import numpy as np
import pandas as pd
from Update_rule import Update_rule
from Util import *
from Est_parallel import *
from ENV import ENV
from scipy.optimize import minimize
import copy ,time,datetime
from collections import defaultdict,OrderedDict
from functools import partial
from scipy.stats import norm
#from scipy.stats import multivariate_normal
import multiprocessing

from functools import partial
from contextlib import contextmanager
import pickle as pk
import quantecon  as qe
from numpy import linalg as LA





Simu_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.15,
        "priv_var":0.1,
        "epsilon_var":0.1, 
        }

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)
   






def GMM_Ineq(Theta0,Est_data,d_struct):
    Theta={
    "comm_mu":Theta0[0],
    "priv_mu":Theta0[1],
    "comm_var":Theta0[2],
    "priv_var":Theta0[3],
    "epsilon_var":Theta0[4],
    }
    

    rng=np.random.RandomState(d_struct['rng_seed'])
    

    start = time.time()
    
    
    print('--------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
#    print('# of auctions: '+str(TT) )
    
    JJ    =d_struct["JJ"]
    Mom_v =0
    
    nn=len(Est_data)
    
    DATA_STRUCT_c = balance_data_est(Est_data,4)
    for Data_struct in DATA_STRUCT_c:
        TT,_=Data_struct.shape
        
        # TT,T_end=Data_struct.data_act.shape
        # TT = int(TT)
        # T_end=int(T_end)
    
        # # num of bidders in the auction
        # N=int(Data_struct.pub_info[1,2])
        # info_flag=Data_struct.pub_info[1,3]
        # # setup the env info structure
        
        # Env=ENV(N, Theta)
    
        # if info_flag == 0 :
        #     para=Env.Uninform()
        # else:
        #     para=Env.Info_ID()
        
        
        # [x_signal,w_x]=signal_DGP(para,res,rng,N,JJ)
        
        '''
        serial testing 
        '''
        func=partial(para_fun_est,Theta,rng,JJ)
        results=[]
        pub_col=['ladder_norm', 'win_norm', 'real_num_bidder','priority_people', 'res_norm']
        for arg_data_ele in zip(range(0,TT),Data_struct['bidder_state'],Data_struct['bidder_pos'],Data_struct['price_norm'],Data_struct[pub_col].values.tolist()):
            results.append(func(arg_data_ele))
    
        MoM=np.nansum(results)/TT
        
        Mom_v=Mom_v+MoM
        
    auction_result=Mom_v/nn



    # '''
    # serial testing for map 
    # '''
    # func=partial(para_fun,para,info_flag,rng,T_end,int(JJ*N),x_signal,w_x)
    # results=list(map(func, zip(range(0,TT), Data_struct.data_act,Data_struct.data_state,Data_struct.pub_info) ))
    
    # MoM=sum(results)/TT
    
    end = time.time()
    
    print("object value : "+ str(auction_result) )
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
    
    ## save the parameters and objective value 
    
    with open('para1.txt', 'a+') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("%f\n" % auction_result)
    
    return auction_result



if __name__ == '__main__':
    
    Est_data=pd.read_hdf('G:/auction/clean/est.h5',key='test_raw')
    # Est_data=pd.read_hdf(data_path+'est.h5',key='test_raw')
    est_data=pre_data(Est_data)
    # set up the hyper parameters
    rng_seed=789
    SS=25
    JJ=400
    
    
    d_struct={
            'rng_seed':rng_seed,
            'SS':SS,
            "JJ":JJ,
            }
    

    Theta=[0.1,0.05,0.3,0.1,0.2]
    
    start = time.time()
    now = datetime.datetime.now()
    print("------------------------------------------------------------------")
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq, Theta, method='Nelder-Mead',args=(est_data,d_struct)) 
    
    print("------------------------------------------------------------------")
    now = datetime.datetime.now()
    end = time.time()
    print("optimization ends at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("time spending is : %f minutes"  % ((end-start)/60) )
    print("------------------------------------------------------------------")
    print("\n\n\nFinal Output : \n")
    print(res)
    print(res.message)
    print(res.x)
            



