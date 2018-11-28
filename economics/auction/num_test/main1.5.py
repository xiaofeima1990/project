# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 18:34:21 2018

@author: mgxgl

new modification :
    I believe inorder to fit the high dimentionality problems. the QMC may be 
    the better choice for me 
    the grid point should be either 
    * lattices
    * sparse grid
    
    make the integ part matrix
    make map inthe thread part     
    
"""

import os 
import sys


sys.path.append('/storage/work/g/gum27/system/pkg/')

'''
install the package :
    eg. I am in the work directory and want to install on the pkg 
    pip install --target=system/pkg/ package_name

'''




import numpy as np
from simu import Simu
from Update_rule import Update_rule
from est import Est
from ENV import ENV
from scipy.optimize import minimize
import time,datetime

from functools import partial
from scipy.stats import norm
#from scipy.stats import multivariate_normal
import multiprocessing
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading

from contextlib import contextmanager
import pickle as pk
import quantecon  as qe
from numpy import linalg as LA
from para_run import *




Simu_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }


   
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()




def signal_DGP_parallel(public_info,para,rng,N,JJ=15):
    

    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
    pub_mu = public_info[0]
    
    # random reservation ratio
    # r =  0.8 + 0.1*self.rng.rand() 
    r =  public_info[1]
    
    

#    x_signal=rng.multivariate_normal(MU.flatten(),SIGMA2,JJ)
    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
    info_index=public_info[3]
    
#    prob_x_signal=multivariate_normal.pdf(x_signal,MU.flatten(),SIGMA2)
    
    
    
    return [pub_mu,x_signal,w_x,info_index,r]

def signal_DGP(para,rng,N,JJ=400):


    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
#    pub_mu = public_info[0]
    
    # random reservation ratio
#    r =  public_info[1]
    
    
    # Cholesky Decomposition
    lambda_0,B=LA.eig(SIGMA2)
    lambda_12=lambda_0**(0.5)
    Sigma=B@np.diag(lambda_12)@LA.inv(B)
    
    # lattices 
    [xi_n,w_n]=qe.quad.qnwequi(int(JJ*N),np.zeros(N),np.ones(N),kind='R',random_state=rng)
    
    a_n= norm.ppf(xi_n)
    
    x_signal= Sigma@a_n.T +MU@np.ones([1,int(JJ*N)])
    x_signal= x_signal.T

#    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
#    info_index=public_info[3]
    
    
    return [x_signal,w_n]






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

    '''
    parallel programming with two levels
        data separating
        runing the estimation
    '''
    data_n=len(DATA_STRUCT)
    
    work_pool = ThreadPoolExecutor(max_workers=data_n)
    
    cpu_num=multiprocessing.cpu_count()
    
    cpu_num_node=int((cpu_num-1)/data_n)
    # change the submit to mpa so that we can run multi-part altogether
    auction_list=work_pool.map(partial(para_data_allo_1,Theta, cpu_num_node,rng,d_struct),iter(DATA_STRUCT))
    
    auction_result=np.nanmean(list(auction_list))
    
    end = time.time()
    
    print("object value : "+ str(auction_result) )
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
    
    ## save the parameters and objective value 
    
    with open('para.txt', 'a+') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("%f\t" % auction_result)
        f.write("%f\n" % (end - start)/60)
    
    return auction_result


def para_data_allo_1(Theta,cpu_num, rng, d_struct, Data_struct):
    time.sleep(1)
    pub=Data_struct.pub_info[0,]
    
    print(" id: {} , is dealing the auction with {} bidder ".format(threading.get_ident(),pub[2]))
    
    
    
    
    JJ    =d_struct["JJ"]
    
    # number of auctions in the data || maximum length of an auction
    
    TT,T_end=Data_struct.data_act.shape
    TT    = int(TT)
    T_end = int(T_end)
    
    '''
    
    take the grid generation outsides
    
    '''
    
    # num of bidders in the auction
    N=int(pub[2])
    
    # setup the env info structure
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
    
    start = time.time()
    results= pool.map(func, zip(range(0,TT), Data_struct.data_act,Data_struct.data_state,Data_struct.pub_info))

    MoM=np.nanmean(list(results))
    
    end = time.time()
    print('time expenditure for the auction estimation under N = {}'.format(N))
    print(end - start)
    
    return MoM

           


if __name__ == '__main__':
    
    # load the data

    simu_data = pk.load( open( "simu_data_est.pkl", "rb"))
    print("the total chunk of the input data is {}".format(len(simu_data)))
    
    # set up the hyper parameters
    rng_seed=789
    SS=25
    JJ=300

    #est=Est(N,rng_seed,TT,SS,info_flag)
    
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
