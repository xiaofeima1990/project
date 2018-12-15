# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 00:42:03 2018


@author: mgxgl

new modification :
    I believe inorder to fit the high dimentionality problems. the QMC may be 
    the better choice for me 
    the grid point should be either 
    * lattices
    * sparse grid
    
    make the integ part matrix
    
    
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

data_path= os.path.dirname(PATH) + '/data/Simu/'


import numpy as np
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






Simu_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }

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
    "priv_mu":Theta0[1],
    "epsilon_mu":Theta0[2],
    "comm_var":Theta0[3],
    "priv_var":Theta0[4],
    "epsilon_var":Theta0[5],
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
    data_n=len(DATA_STRUCT)
    
    num_works = 6 
    work_pool = ThreadPoolExecutor(max_workers=num_works)
    
    cpu_num=multiprocessing.cpu_count()
    cpu_num_node=int((cpu_num-num_works)/data_n)
    
    auction_list=[]
    # balance each work pool tasks: 
    # make data similar rather than sequencially run # 3, 4, 5, 6, 7, ...
    

    for Data_Struct in DATA_STRUCT:
     

        auction_list.append(work_pool.submit(partial(para_data_allo_1,Theta, cpu_num_node,rng,d_struct),Data_Struct).result())
    
    
    auction_result=np.nanmean(auction_list)
    
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


def para_data_allo_1(Theta,cpu_num, rng, d_struct, Data_struct):
    time.sleep(1)
    pub=Data_struct.pub_info[0,]
    
    print(" id: {} , is dealing the auction with {} bidder ".format(threading.get_ident(),pub[2]))
    
    
    
    
    JJ    =d_struct["JJ"]
    
    TT,T_end=Data_struct.data_act.shape
    TT = int(TT)
    T_end=int(T_end)
    print("the length of the auction is {}".format(TT))
    
    '''
    
    take the grid generation outsides
    
    '''
    
    # num of bidders in the auction
    N=int(pub[2])
    info_flag=pub[3]
    # setup the env info structure
    
    Env=ENV(N, Theta)

    if info_flag == 0 :
        para=Env.Uninform()
    else:
        para=Env.Info_ID()
    
    
    [x_signal,w_x]=signal_DGP(para,rng,N,JJ)
    
    results=[]
    
    
    func=partial(para_fun,para,info_flag,rng,T_end,int(JJ*N),x_signal,w_x)

    pool = ProcessPoolExecutor(max_workers=cpu_num)
    
    
    results= pool.map(func, zip(range(0,TT), Data_struct.data_act,Data_struct.data_state,Data_struct.pub_info))
    
    
    MoM=sum(results)/TT
    
    
    return MoM

     
                
           


if __name__ == '__main__':
    
    
    # load the data

    simu_data = pk.load( open( "simu_data_est.pkl", "rb"))
    print("the total chunk of the input data is {}".format(len(simu_data)))
    
    # set up the hyper parameters
    rng_seed=789
    SS=25
    JJ=300
    
    
    d_struct={
            'rng_seed':rng_seed,
            'SS':SS,
            "JJ":JJ,
            }
    

    Theta=[10,1,0,0.8,1.2,0.8]
    
    start = time.time()
    now = datetime.datetime.now()
    print("------------------------------------------------------------------")
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq_parall, Theta, method='nelder-mead',args=(simu_data,d_struct)) 
    
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
