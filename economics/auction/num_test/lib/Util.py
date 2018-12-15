# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 13:29:54 2018

@author: mgxgl
This contains the method dealing with the data balance, formating etc...
 

"""

import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')


import numpy as np
from simu import Simu,data_struct
from Update_rule import Update_rule

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






def balance_data(DATA_STRUCT,n_work):
    data_n=len(DATA_STRUCT)
    Data_Struct_c=[]
    pecentil_slice=1.0/n_work
    # initialize
    for i in range(n_work):
        temp_dict={}
        T_len=len(DATA_STRUCT[0].data_dict['data_win'])
        start_point=i*int(np.floor(pecentil_slice))
        end_point  =(i+1)*int(np.floor(pecentil_slice)) * 1*(i !=n_work) + T_len * 1*(i ==n_work)

        for key, ele in DATA_STRUCT[0].data_dict.items():
            temp_dict[key]=ele[start_point:end_point,]
    

        Data_Struct_c.append(temp_dict)

    # looping 
    for i in range(n_work):
        for j in range(1,data_n):
            T_len=len(DATA_STRUCT[j].data_dict['data_win'])
            start_point=i*int(np.floor(pecentil_slice))
            end_point  =(i+1)*int(np.floor(pecentil_slice)) * 1*(i !=n_work) + T_len * 1*(i ==n_work)


            for key, ele in DATA_STRUCT[j].data_dict.items():
                Data_Struct_c[i][key]=np.append(Data_Struct_c[i][key],ele[start_point:end_point,], axis=0)
    # turn to the data_struct

    return [data_struct(ele) for ele in Data_Struct_c ]


def signal_DGP_parallel(public_info,para,rng,N,JJ=15):
    

    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
    pub_mu = public_info[0]
    
    # random reservation ratio
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


