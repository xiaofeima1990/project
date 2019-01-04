# -*- coding: utf-8 -*-
"""
Created on 12-14-2018 
This is used for testing the estimation program
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

data_path= os.path.dirname(PATH) + '/data/Simu/'



import numpy as np
from simu import Simu
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

# def signal_DGP(para,rng,N,JJ=400):


    
#     MU       =para.MU
#     SIGMA2   =para.SIGMA2
#     # common value in public
# #    pub_mu = public_info[0]
    
#     # random reservation ratio
# #    r =  public_info[1]
    
    
#     # Cholesky Decomposition
#     lambda_0,B=LA.eig(SIGMA2)
#     lambda_12=lambda_0**(0.5)
#     Sigma=B@np.diag(lambda_12)@LA.inv(B)
    
#     # lattices 
#     [xi_n,w_n]=qe.quad.qnwequi(int(JJ*N),np.zeros(N),np.ones(N),kind='R',random_state=rng)
    
#     a_n= norm.ppf(xi_n)
    
#     x_signal= Sigma@a_n.T +MU@np.ones([1,int(JJ*N)])
#     x_signal= x_signal.T

# #    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
# #    info_index=public_info[3]
    
    
#     return [x_signal,w_n]






def GMM_Ineq(Theta0,DATA_STRUCT,d_struct):
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
    
    JJ    =d_struct["JJ"]
    Mom_v =0
    
    nn=len(DATA_STRUCT)
    
    DATA_STRUCT_c = balance_data(DATA_STRUCT,4)
    for Data_struct in DATA_STRUCT_c:
        TT,T_end=Data_struct.data_act.shape
        TT = int(TT)
        T_end=int(T_end)
    
        # num of bidders in the auction
        N=int(Data_struct.pub_info[1,2])
        info_flag=Data_struct.pub_info[1,3]
        # setup the env info structure
        
        Env=ENV(N, Theta)
    
        if info_flag == 0 :
            para=Env.Uninform()
        else:
            para=Env.Info_ID()
        
        
        [x_signal,w_x]=signal_DGP(para,rng,N,JJ)
    
        
        '''
        serial testing 
        '''
        func=partial(para_fun,para,info_flag,rng,T_end,int(JJ*N),x_signal,w_x)
        results=0
        for arg_data_ele in zip(range(0,TT), Data_struct.data_act,Data_struct.data_state,Data_struct.pub_info):
            results=results+func(arg_data_ele)
    
        MoM=results/TT
        
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
    
    
    # load the data
    with open( data_path + "simu_data_uninfo.pkl", "rb") as f :
        simu_data=pk.load( f)
#    simu_data = pk.load( open( "simu_data_est.pkl", "rb"))
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
    

    Theta=[10,1,0,0.15,0.1,0.1]
    
    start = time.time()
    now = datetime.datetime.now()
    print("------------------------------------------------------------------")
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq, Theta, method='nelder-mead',args=(simu_data[:2],d_struct)) 
    
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
