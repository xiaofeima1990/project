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


def balance_data_est(Est_data,n_work):
    pecentil_slice=1.0/n_work
    Data_Struct_c=[]
    # initialize
    group_est=Est_data.groupby('num_bidder')
    for i in range(n_work):
        
        temp_df=group_est.get_group(2)
        T_len=len(temp_df)
        start_point=i*int(np.floor(pecentil_slice*T_len)) 
        end_point  =(i+1)*int(np.floor(pecentil_slice*T_len)) * 1*(i !=n_work) + T_len * 1*(i ==n_work)

        Data_Struct_c.append(temp_df.iloc[start_point:end_point,])

    # looping
    for key in group_est.groups.keys():
        if key >2: 

            for i in range(n_work):
                temp_df=group_est.get_group(key)
                T_len=len(temp_df)
                start_point=i*int(np.floor(pecentil_slice*T_len)) 
                end_point  =(i+1)*int(np.floor(pecentil_slice*T_len)) * 1*(i !=n_work) + T_len * 1*(i ==n_work)

                Data_Struct_c[i]=Data_Struct_c[i].append(temp_df.iloc[start_point:end_point,],ignore_index=True)


    return Data_Struct_c



def balance_data(DATA_STRUCT,n_work):
    data_n=len(DATA_STRUCT)
    Data_Struct_c=[]
    pecentil_slice=1.0/n_work
    # initialize
    for i in range(n_work):
        temp_dict={}
        T_len=len(DATA_STRUCT[0].data_dict['data_win'])
        start_point=i*int(np.floor(pecentil_slice*T_len)) 
        end_point  =(i+1)*int(np.floor(pecentil_slice*T_len)) * 1*(i !=n_work) + T_len * 1*(i ==n_work)

        for key, ele in DATA_STRUCT[0].data_dict.items():
            temp_dict[key]=ele[start_point:end_point,]
    

        Data_Struct_c.append(temp_dict)
        

    # looping 
    for i in range(n_work):
        for j in range(1,data_n):
            T_len=len(DATA_STRUCT[j].data_dict['data_win'])
            start_point=i*int(np.floor(pecentil_slice*T_len)) 
            end_point  =(i+1)*int(np.floor(pecentil_slice*T_len)) * 1*(i !=n_work) + T_len * 1*(i ==n_work)

            for key, ele in DATA_STRUCT[j].data_dict.items():
                r_1,c_1 = Data_Struct_c[i][key].shape
                _,c_2 = ele[start_point:end_point,].shape
                if c_1 < c_2:
                    extra_array=np.ones([r_1,c_2-c_1])*(-1)
                    temp_array =np.hstack((Data_Struct_c[i][key],extra_array))
                else:
                    temp_array =Data_Struct_c[i][key]
                Data_Struct_c[i][key]=np.append(temp_array, ele[start_point:end_point,], axis=0)



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



def signal_DGP_est(para,res,rng,N,JJ=400):


    
    MU       =para.MU+res
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




'''
Data preprocessing
'''

    

def price_norm(arg):
    return arg['bidder_price']/arg['evaluation_price']



def pre_data(Est_data):
    col_name=['ID', 'bidder_act', 'len_act', 'bidder_pos', 'bidder_state','bidder_price','ladder_norm',
              'win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
    # get rid of number of bidder = = 1
    Est_data=Est_data[Est_data['num_bidder']>1]
    Est_data=Est_data[Est_data['num_bidder']<=8]
    Est_data=Est_data[Est_data['len_act']>2]

    # double check
    Est_data['len_state']= Est_data['bidder_state'].apply(lambda x: len(x))
    Est_data=Est_data[Est_data['len_state']>1]
    Est_data=Est_data[Est_data['len_state']<=8]
    # get rid of priority people
    Est_data=Est_data[Est_data['priority_people']==0]
    
    
    # normalize reservation price
    Est_data['res_norm']=Est_data['reserve_price']/Est_data['evaluation_price']
    Est_data = Est_data[np.isfinite(Est_data['res_norm'])]
    Est_data=Est_data.dropna(subset=['res_norm'])
    # normalize the win bid
    Est_data['win_norm']=Est_data['win_bid']/Est_data['evaluation_price']
    
    # normalize bid ladder 
    Est_data['ladder_norm']=Est_data['bid_ladder']/Est_data['evaluation_price']
    
    Est_data['bidder_price']=Est_data['bidder_price'].apply(lambda x: np.array(x) )
    Est_data['price_norm'] = Est_data.apply(price_norm,axis= 1 )
    
    
    
    return Est_data[col_name]
                
           