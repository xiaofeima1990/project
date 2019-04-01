# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 18:42:03 2018

@author: mgxgl

use real data to do the parallel estimation 

This is used for MLE estimation test
I have three different MLE method. 
omega   : Prob(Xi in [xi_low, xi_up] | Omega_it xj in [xj_low,xj_up])
omega2  : Prob(Xi not in [xi_low, xi_up] | Omega_it xj in [xj_low,xj_up])
karl    : Prob_Xi (Xi in [X_low, X_up] | Xi > gamma) 

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
from Update_rule3 import Update_rule
from Est_parallel3 import *
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
from numpy import linalg as LA
import warnings
warnings.filterwarnings("default")
# error ignore default module once


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

def GMM_Ineq_parall(Theta0,Data_struct,d_struct):
    Theta={
    "comm_mu":Theta0[0],
    # "epsilon_mu":Theta0[1], # change from private mu to epsilon_mu
    "beta":Theta0[1],
    "comm_var":Theta0[2],
    "priv_var":Theta0[3],
    "epsilon_var":Theta0[4],
    }
    

    rng=np.random.RandomState(d_struct['rng_seed'])
    start = time.time()
    
    
    print('------------------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
#    print('# of auctions: '+str(TT) )

    '''
    parallel programming with two levels
        data separating
        runing the estimation
    '''
    if Theta['priv_var'] <=0 or Theta['epsilon_var']<=0 or Theta['comm_var']<=0 :
    	print('variance <0 ')
    	return 10000
    if Theta['epsilon_var'] >1 or Theta['comm_var'] > 1 or Theta['beta']<0 :
        print('variance > 1 or beta <0')
        return 10000
    # if is_pos_def(Theta,d_struct['max_N']) :
    #     print("not positive definite variance matrix")
    #     return 10000
    
    cpu_num=multiprocessing.cpu_count()
    print("num of cpu is "+str(cpu_num))

    TT,_=Data_struct.shape
    print("the length of the auction is {}".format(TT))
    
    try:
        
        func=partial(para_fun_est,Theta,rng,d_struct)
        pool = ProcessPoolExecutor(max_workers=cpu_num)
        results= pool.map(func, zip(range(0,TT), Data_struct['bidder_state'],Data_struct['bidder_pos'],Data_struct['price_norm'],Data_struct[Pub_col].values.tolist() ) )
        MoM=np.nanmean(np.array(list(results)).flatten())

    except np.linalg.LinAlgError as err:
        if 'Singular matrix' in str(err):
            return 10**5
        else:
            print(err)
            exit(1)


    auction_result=np.asscalar(MoM)
    
    end = time.time()
    
    print("object value : "+ str(auction_result) )
    print("time spend in this loop: ")
    print(end - start)
    print('------------------------------------------------------------------\n')
    
    ## save the parameters and objective value 
    
    with open('para_est-new.txt', 'a+') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("{0:.8f}\n".format(auction_result))
    
    return auction_result




if __name__ == '__main__':
    
    
    # load the data
    Est_data=pd.read_hdf(data_path+'est.h5',key='test_raw')
    # clean the data
    Est_data=pre_data(Est_data)
    # set up the hyper parameters
    rng_seed=1234
    max_N = 10
    JJ    = 5000
    
    d_struct={
            'rng_seed':rng_seed,
            "max_N":max_N,
            'model_flag':1,
            'MLE_choice':3,
            'h':0.05,
            }
    
    Theta=[0.008128,	1.124905,	0.173707,	0.001357,	0.137546]
    
    start = time.time()
    now = datetime.datetime.now()
    bnds = ((0, 2), (-1, 1), (0,2), (0,2), (0,2))
    print('------------------------------------------------------------------')
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq_parall, Theta, method='Nelder-Mead',args=(Est_data,d_struct)) 
    
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
            






#Nelder-Mead
#Powell
#CG
#BFGS
#Newton-CG 
#L-BFGS-B 
#TNC 
#COBYLA 
#SLSQP
#trust-constr
#dogleg
#trust-ncg
#trust-exact 
#trust-krylov 
