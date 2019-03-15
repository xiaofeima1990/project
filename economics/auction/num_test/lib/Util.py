# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 13:29:54 2018

@author: mgxgl
This contains the method dealing with the data balance, formating etc...
 

"""

import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')


import numpy as np
# from simu import Simu,data_struct
# from Update_rule2 import Update_rule
import scipy.linalg as LAA
from functools import partial
from scipy.stats import norm,truncnorm
import pickle as pk
import quantecon  as qe
from numpy import linalg as LA

# I need to make sure descending order 
# is_sorted = lambda a: np.all(a[:-1] >= a[1:])
# it is very hard to guarantee the ordered case 
# So I choose to treat the  order into the first guy is the highest 
is_sorted = lambda a: np.all(a[0] >= a[1:])  # Test for first position is the highest valued bidder
is_sorted2 = lambda a: np.all(a[1] >= a[2:]) # Test for the second position is the second highest valued bidder
is_sorted3 = lambda a: np.all(a[-1] <= a[0:-1]) # Test for the last position is the lowest valued bidder 
def balance_data_est(Est_data,n_work):
    pecentil_slice=1.0/n_work
    Data_Struct_c=[]
    # initialize
    group_est=Est_data.groupby('num_bidder')
    min_key=min(list(group_est.groups.keys()))
    for i in range(n_work):
        
        temp_df=group_est.get_group(min_key)
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

def rng_generate(rng,JJ=10000,N_max=10,loc=-0.1):
    # I believe I have to use truncated stanard normal to generate the results 
    xi_n = truncnorm.rvs(0,1,loc,size=int(JJ*N_max),random_state=rng)
    xi_n = xi_n.reshape(JJ,N_max)
    # [xi_n,w_n]=qe.quad.qnwequi(int(JJ*N_max),np.zeros(N_max),np.ones(N_max),kind='N',random_state=rng )
    # a_n= norm.ppf(xi_n)
    
    # order
    x_check_f=np.apply_along_axis(is_sorted,1,xi_n)
    xi_n=xi_n[x_check_f,]
    # x_check_f=np.apply_along_axis(is_sorted2,1,xi_n)
    # xi_n=xi_n[x_check_f,]
    # x_check_f=np.apply_along_axis(is_sorted3,1,xi_n)
    # xi_n=xi_n[x_check_f,]

    return xi_n

def signal_DGP_est(para,rng,N,i_id,X_bar,X_up,xi_n):
    # this part should follow the ascending order 
    # X_bar is the threshold 
    

    MU       =para.MU[i_id] 
    MU       =MU.reshape(N,1)
    SIGMA2   =para.SIGMA2[i_id]
    
    # use scipy to comput the square root of Sigma
    [D,V]=LA.eig(SIGMA2)
    D_root = D**0.5
    Sigma = V @ np.diag(D_root) @ LA.inv(V)
    Sigma=Sigma.real

    # Sigma=LAA.sqrtm(SIGMA2)
    # Sigma=Sigma.real

    # lattices 
    # [xi_n,w_n]=qe.quad.qnwequi(int(JJ),np.zeros(N),np.ones(N),kind='N',random_state=rng )
    r,n=xi_n.shape
    a_n = xi_n[:,0:N]
    
    x_signal= Sigma@a_n.T +MU@np.ones([1,r])
    x_signal= x_signal.T


    # entry selection 
    X_bar = X_bar.reshape(1,N)
    check_flag = x_signal >= X_bar
    check_flag_v=np.prod(check_flag, axis=1)
    # check_flag2 = x_signal <= X_up
    # check_flag_v2=np.prod(check_flag2, axis=1)

    # check_flag_v=check_flag_v*check_flag_v2
    check_flag_v=check_flag_v.astype(bool)
    x_signal=x_signal[check_flag_v,]

    # x_check_f=np.apply_along_axis(is_sorted3,1,x_signal)
    # x_signal=x_signal[x_check_f,]

    if x_signal.shape[0] >150:
        x_signal=x_signal[np.random.choice(x_signal.shape[0], 150, replace=False), :]

    return x_signal




'''
Data preprocessing
'''


def pre_data(Est_data,max_N=10):
    col_name=['ID', 'bidder_act', 'len_act', 'bidder_pos', 'bidder_state','bidder_price','ladder_norm',
              'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
    # get rid of number of bidder = = 1
    Est_data=Est_data[Est_data['num_bidder']>1]
    Est_data=Est_data[Est_data['num_bidder']<=max_N]
    Est_data=Est_data[Est_data['len_act']>2]

    # double check
    Est_data['real_num_bidder']= Est_data['bidder_state'].apply(lambda x: len(x))
    Est_data=Est_data[Est_data['real_num_bidder']>1]
    Est_data=Est_data[Est_data['real_num_bidder']<=max_N]
    # get rid of priority people
    Est_data=Est_data[Est_data['priority_people']==0]
    
    
    # normalize reservation price
    Est_data['res_norm']=Est_data['reserve_price']/Est_data['evaluation_price']
    Est_data = Est_data[np.isfinite(Est_data['res_norm'])]
    Est_data=Est_data.dropna(subset=['res_norm'])
    Est_data=Est_data[Est_data['res_norm'] >= 0.7]
    # normalize the win bid
    Est_data['win_norm']=Est_data['win_bid']/Est_data['reserve_price']
    tail=Est_data['win_norm'].quantile(0.95)
    Est_data=Est_data[Est_data['win_norm']<=tail]
    # normalize bid ladder 
    Est_data['ladder_norm']=Est_data['bid_ladder']/Est_data['evaluation_price']
    
    Est_data['bidder_price']=Est_data['bidder_price'].apply(lambda x: np.array(x) )
    Est_data['price_norm'] = Est_data['bidder_price']/Est_data['evaluation_price']
    # delete the abnormal point
    # Est_data=Est_data.reset_index(drop=True)
    # Est_data=Est_data.drop(Est_data.index[537])
    # Est_data=Est_data.reset_index(drop=True)
#    Est_data=Est_data[Est_data['real_num_bidder']>=6]
    return Est_data[col_name]

def pre_data_stage1(Est_data,max_N=10,info_flag=0):
    col_name=['ID', 'bidder_act', 'len_act', 'bidder_pos', 'bidder_state','bidder_price','ladder_norm',
              'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
    # priority people
    Est_data=Est_data[Est_data['priority_people']==info_flag]
    # get rid of number of bidder = = 1
    Est_data=Est_data[Est_data['num_bidder']>1]
    Est_data=Est_data[Est_data['num_bidder']<=max_N]
    Est_data=Est_data[Est_data['len_act']>2]

    # double check
    Est_data['real_num_bidder']= Est_data['bidder_state'].apply(lambda x: len(x))
    Est_data=Est_data[Est_data['real_num_bidder']>1]
    Est_data=Est_data[Est_data['real_num_bidder']<=max_N]

    
    
    # normalize reservation price
    Est_data['res_norm']=Est_data['reserve_price']/Est_data['evaluation_price']
    Est_data = Est_data[np.isfinite(Est_data['res_norm'])]
    Est_data=Est_data.dropna(subset=['res_norm'])
    Est_data=Est_data[Est_data['res_norm'] >= 0.7]
    # normalize the win bid
    Est_data['win_norm']=Est_data['win_bid']/Est_data['reserve_price']
    tail=Est_data['win_norm'].quantile(0.95)
    Est_data=Est_data[Est_data['win_norm']<=tail]
    # normalize bid ladder 
    Est_data['ladder_norm']=Est_data['bid_ladder']/Est_data['evaluation_price']
    
    Est_data['bidder_price']=Est_data['bidder_price'].apply(lambda x: np.array(x) )
    Est_data['price_norm'] = Est_data['bidder_price']/Est_data['evaluation_price']

    return Est_data[col_name]


def is_pos_def(Theta,N):
    flag=True
    for n in range(2,N):
        temp_matrix= np.ones((n,n))*Theta['comm_var'] + np.eye(n)*(Theta['priv_var']+Theta['epsilon_var'])    
        # check whether all the n are positive definite
        if not np.all(LA.eigvals(temp_matrix) > 0):
            flag=False


    return flag