# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 11:12:27 2019

@author: xiaofeima
this is used for subsampling my weird estimation results

In CT 2009, I found that they draw R=100 subsample with each n/4 size.

At first I can do 20 

"""
import matplotlib.pyplot as plt
import pickle as pk
import os,sys
sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))
lib_path= os.path.dirname(PATH) + '/lib/'
# lib_path= PATH + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Est/'


import numpy as np
import pandas as pd
from Update_rule2 import Update_rule
from Util import *
from Est_parallel2 import *
from ENV import ENV
from scipy.optimize import minimize
import copy ,time,datetime
from collections import defaultdict,OrderedDict
from functools import partial
from scipy.stats import norm
#from scipy.stats import multivariate_normal
import multiprocessing
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
from contextlib import contextmanager
from numpy import linalg as LA

Pub_col=['ladder_norm', 'win_norm', 'real_num_bidder','priority_people', 'res_norm']


@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


def subsample_data(Est_data,size=300):
    return Est_data.loc[np.random.choice(Est_data.index, size, replace=False),]


def parallel_work(Est_data,Theta,xi_n,d_struct):
    num_works = 5
    work_pool = ThreadPoolExecutor(max_workers=num_works)
    
    cpu_num=multiprocessing.cpu_count()
    cpu_num_node=int((cpu_num-num_works)/num_works)
    
    auction_list=[]
    # balance each work pool tasks: 
    # make data similar rather than sequencially run # 3, 4, 5, 6, 7, ...
    start = time.time()
    now = datetime.datetime.now()
    for i in range(5):
        est_data_sub=subsample_data(est_data,int(len(est_data)/4))

        auction_list.append(work_pool.submit(partial(Opt_min,Theta,d_struct,xi_n,cpu_num_node,i),est_data_sub).result())
    
    end = time.time()
    print('total time consuming for subsampling is {}'.format((end-start)/60))


def Opt_min(Theta,d_struct,xi_n,cpu_num,i_subsample,est_data_sub):
    start = time.time()
    now = datetime.datetime.now()
    print("------------------------------------------------------------------")
    print("optimization Begins(Nelder) at subsample "+str(i_subsample) +": "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq, Theta, method='Nelder-Mead',args=(est_data_sub,d_struct,xi_n,cpu_num,i_subsample)) 
    
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
            


def GMM_Ineq(Theta0,Data_struct,d_struct,xi_n,cpu_num,i_subsample):
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
    print('-----------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)

    TT=Data_struct.shape[0]    
    print("total data size is {}".format(TT))
    try:
        func=partial(para_fun_est,Theta,rng,xi_n,d_struct['h'])

        pool = ProcessPoolExecutor(max_workers=cpu_num)
        
        results= pool.map(func, zip(range(0,TT), Data_struct['bidder_state'],Data_struct['bidder_pos'],Data_struct['price_norm'],Data_struct[Pub_col].values.tolist()))
        
        MoM=np.nanmean(list(results))
        auction_result=MoM

    except np.linalg.LinAlgError as err:
        if 'Singular matrix' in str(err):
            return 10**5
        else:
            print(err)
            exit(1)
    
    end = time.time()
    
    print("object value : "+ str(auction_result) )
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
    
    ## save the parameters and objective value 
    
    with open('subsample_'+str(i_subsample)+'.txt', 'a+') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("%f\n" % auction_result)
    
    return auction_result




if __name__ == '__main__':
            
    # subsampling https://stackoverflow.com/questions/18713929/subsample-pandas-dataframe
    # df.sample
    # sample(self, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None) method of pandas.core.frame.DataFrame instance
    # Returns a random sample of items from an axis of object.
    
    Est_data=pd.read_hdf(data_path+'est.h5',key='test_raw')
    est_data=pre_data(Est_data)
    # set up the hyper parameters
    rng_seed=789
    max_N = 10
    JJ    = 5000
    
    d_struct={
            'rng_seed':rng_seed,
            "max_N":max_N,
            'h':0.05,
            }
    

    Theta=[0.001422,0.8,0.033803,0.0170,0.09089] 
    xi_n =rng_generate(np.random.RandomState(rng_seed),JJ,max_N)

    parallel_work(est_data,Theta,xi_n,d_struct)
