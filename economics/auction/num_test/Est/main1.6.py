# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 18:42:03 2018


@author: mgxgl

use real data to do the parallel estimation 

"""

import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')

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
from simu import Simu,data_struct
from Update_rule import Update_rule
from Est_parallel import *
from Util import *
from ENV import ENV
from scipy.optimize import minimize
import copy ,time,datetime
from collections import defaultdict,OrderedDict
from functools import partial
from scipy.stats import norm

import multiprocessing
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
from functools import partial
from contextlib import contextmanager
import pickle as pk
import quantecon  as qe
from numpy import linalg as LA






Est_para_dict={

        "comm_mu":0.1,
        "priv_mu":0,
        'epsilon_mu':0.1,
        "comm_var":0.05,
        "priv_var":0.1,
        "epsilon_var":0.3,
        }

Pub_col=['ladder_norm', 'win_norm', 'real_num_bidder','priority_people', 'res_norm']

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)
   
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()





def GMM_Ineq_parall(Theta0,DATA_STRUCT,d_struct):
    Theta={
    "comm_mu":Theta0[0],
    # "epsilon_mu":Theta0[1], # change from private mu to epsilon_mu
    # "beta":Theta0[2],
    "comm_var":Theta0[1],
    "priv_var":Theta0[2],
    "epsilon_var":Theta0[3],
    }
    

    rng=np.random.RandomState(d_struct['rng_seed'])
    

    start = time.time()
    
    
    print('--------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
#    print('# of auctions: '+str(TT) )

    '''
    parallel programming with two levels
        data separating
        runing the estimation
    '''
    if Theta['priv_var'] <=0 or Theta['epsilon_var']<=0 or Theta['comm_var']<=0 :
    	print('variance can not be negative')
    	return 10000
    # if Theta['comm_mu'] <=-3 or Theta['priv_mu']<= -3 :
    #     print('mean can not be so negative')
    #     return 10000

    data_n=len(DATA_STRUCT)
    
    num_works = 4
    work_pool = ThreadPoolExecutor(max_workers=num_works)
    
    # reorganize the data
    DATA_STRUCT_c = balance_data_est(Est_data,num_works)
    
    cpu_num=multiprocessing.cpu_count()
    cpu_num_node=int((cpu_num-num_works)/num_works)
    
    auction_list=[]
    # balance each work pool tasks: 
    # make data similar rather than sequencially run # 3, 4, 5, 6, 7, ...
    

    for Data_Struct in DATA_STRUCT_c:
     

        auction_list.append(work_pool.submit(partial(para_data_allo_1,Theta, cpu_num_node,rng,d_struct),Data_Struct).result())
    
    
    auction_result=np.nanmean(auction_list)
    
    end = time.time()
    
    print("object value : "+ str(auction_result) )
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
    
    ## save the parameters and objective value 
    
    with open('para_est-Nelder.txt', 'a+') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("{0:.12f}\n".format(auction_result))
    
    return auction_result


def para_data_allo_1(Theta,cpu_num, rng, d_struct, Data_struct):
    time.sleep(0.5)
    
    
    # print(" id: {} , is dealing the auction with {} bidder ".format(threading.get_ident(),pub[2]))
    
    
    
    
    JJ    =d_struct["JJ"]
    
    TT,_=Data_struct.shape

    print("the length of the auction is {}".format(TT))
    
    
    results=[]
    try:
        
        func=partial(para_fun_est,Theta,rng,JJ)

        pool = ProcessPoolExecutor(max_workers=cpu_num)
        
        
        results= pool.map(func, zip(range(0,TT), Data_struct['bidder_state'],Data_struct['bidder_pos'],Data_struct['price_norm'],Data_struct[Pub_col].values.tolist()))
        
        
        MoM=np.nansum(list(results))

    except np.linalg.LinAlgError as err:
        if 'Singular matrix' in str(err):
            return 10**5
        else:
            print(err)
            exit(1)
    
    
    return MoM / TT

 


if __name__ == '__main__':
    
    
    # load the data

    # Est_data=pd.read_hdf('G:/auction/clean/est.h5',key='test_raw')
    Est_data=pd.read_hdf(data_path+'est.h5',key='test_raw')

    Est_data=pre_data(Est_data)
    # set up the hyper parameters
    rng_seed=1234
    SS=25
    JJ=400
    
    
    d_struct={
            'rng_seed':rng_seed,
            'SS':SS,
            "JJ":JJ,
            }
    
    # Theta={
    #     "comm_mu":1, # comman value mu
    #     "priv_mu":0, # private value mu
    #     "beta":0,   # for coefficient in front of the reservation price 
    #     "comm_var":0.1,
    #     "priv_var":0.3,
    #     "epsilon_var":0.4,
    #     }

    Theta=[-0.3,0.25,0.1,0.3]
    
    start = time.time()
    now = datetime.datetime.now()
    bnds = ((0, 2), (-1, 1), (0,2), (0,2), (0,2))

    print("------------------------------------------------------------------")
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq_parall, Theta, method='Nelder-Mead',args=(Est_data,d_struct),bounds=bnds) 
    
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
            







#‘Nelder-Mead’ 
#‘Powell’
#‘CG’
#‘BFGS’
#‘Newton-CG’ 
#‘L-BFGS-B’ 
#‘TNC’ 
#‘COBYLA’ 
#‘SLSQP’ )
#‘trust-constr’
#‘dogleg’ 
#‘trust-ncg’ 
#‘trust-exact’ 
#‘trust-krylov’ 
