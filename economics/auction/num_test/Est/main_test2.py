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

data_path= os.path.dirname(PATH) + '/data/Simu/'



import numpy as np
import pandas as pd
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
#
#def signal_DGP(para,res,rng,N,JJ=400):
#
#
#    
#    MU       =para.MU + res
#    SIGMA2   =para.SIGMA2
#    # common value in public
##    pub_mu = public_info[0]
#    
#    # random reservation ratio
##    r =  public_info[1]
#    
#    
#    # Cholesky Decomposition
#    lambda_0,B=LA.eig(SIGMA2)
#    lambda_12=lambda_0**(0.5)
#    Sigma=B@np.diag(lambda_12)@LA.inv(B)
#    
#    # lattices 
#    [xi_n,w_n]=qe.quad.qnwequi(int(JJ*N),np.zeros(N),np.ones(N),kind='R',random_state=rng)
#    
#    a_n= norm.ppf(xi_n)
#    
#    x_signal= Sigma@a_n.T +MU@np.ones([1,int(JJ*N)])
#    x_signal= x_signal.T
#
##    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
##    info_index=public_info[3]
#    
#    
#    return [x_signal,w_n]






def GMM_Ineq(Theta0,Est_data,d_struct):
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
        pub_col=['ladder_norm', 'win_norm', 'num_bidder','priority_people', 'res_norm']
        for arg_data_ele in zip(range(0,TT),Data_struct['bidder_state'],Data_struct['bidder_pos'],Data_struct['price_norm'],Data_struct[pub_col].values.tolist()):
            results.append(func(arg_data_ele))
    
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


# def price_norm(arg):
#     return arg['bidder_price']/arg['evaluation_price']



# def pre_data(Est_data):
#     col_name=['ID', 'bidder_act', 'len_act', 'bidder_pos', 'bidder_state','bidder_price','ladder_norm',
#               'win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
#     # get rid of number of bidder = = 1
#     Est_data=Est_data[Est_data['num_bidder']>1]
#     Est_data=Est_data[Est_data['num_bidder']<=8]
#     Est_data=Est_data[Est_data['len_act']>2]

#     # double check
#     Est_data['len_state']= Est_data['bidder_state'].apply(lambda x: len(x))
#     Est_data=Est_data[Est_data['len_state']>1]
#     Est_data=Est_data[Est_data['len_state']<=8]
#     # get rid of priority people
#     Est_data=Est_data[Est_data['priority_people']==0]
    
    
#     # normalize reservation price
#     Est_data['res_norm']=Est_data['reserve_price']/Est_data['evaluation_price']
#     # normalize the win bid
#     Est_data['win_norm']=Est_data['win_bid']/Est_data['evaluation_price']
    
#     # normalize bid ladder 
#     Est_data['ladder_norm']=Est_data['bid_ladder']/Est_data['evaluation_price']
    
#     Est_data['bidder_price']=Est_data['bidder_price'].apply(lambda x: np.array(x) )
#     Est_data['price_norm'] = Est_data.apply(price_norm,axis= 1 )
    
    
    
#     return Est_data[col_name]


if __name__ == '__main__':
    
    Est_data=pd.read_hdf('G:/auction/clean/est.h5',key='test_raw')

    est_data=pre_data(Est_data)
    # set up the hyper parameters
    rng_seed=789
    SS=25
    JJ=300
    
    
    d_struct={
            'rng_seed':rng_seed,
            'SS':SS,
            "JJ":JJ,
            }
    

    Theta=[0.1,0.05,0,0.05,0.04,0.04]
    
    start = time.time()
    now = datetime.datetime.now()
    print("------------------------------------------------------------------")
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq, Theta, method='nelder-mead',args=(est_data,d_struct)) 
    
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
            



