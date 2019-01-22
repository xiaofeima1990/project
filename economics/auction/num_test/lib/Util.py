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
import scipy.linalg as LAA
from functools import partial
from scipy.stats import norm
import pickle as pk
import quantecon  as qe
# from numpy import linalg as LA

# I need to make sure descending order 
# is_sorted = lambda a: np.all(a[:-1] >= a[1:])
# it is very hard to guarantee the ordered case 
# So I choose to treat the  order into the first guy is the highest 
is_sorted = lambda a: np.all(a[0] > a[1:])
is_sorted2 = lambda a: np.all(a[1] > a[2:])

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


def signal_DGP_est(para,rng,N,i_id,X_bar,X_up,JJ=400):
    # this part should follow the ascending order 
    # X_bar is the threshold 
    
    MU       =para.MU[i_id] 
    MU       =MU.reshape(N,1)
    SIGMA2   =para.SIGMA2[i_id]

    
    
    # use scipy to comput the square root of Sigma
    Sigma=LAA.sqrtm(SIGMA2)
    Sigma=Sigma.real

    t_count=5
    while t_count>0 :
        # lattices 
        [xi_n,w_n]=qe.quad.qnwequi(int(JJ),np.zeros(N),np.ones(N),kind='N',random_state=rng )
        
        a_n= norm.ppf(xi_n)

        x_signal= Sigma@a_n.T +MU@np.ones([1,int(JJ)])
        x_signal= x_signal.T


        # entry selection 
        X_bar = X_bar.reshape(1,N)
        check_flag = x_signal >= X_bar
        check_flag_v=np.prod(check_flag, axis=1)
        check_flag2 = x_signal <= X_up
        check_flag_v2=np.prod(check_flag2, axis=1)

        check_flag_v=check_flag_v*check_flag_v2
        check_flag_v=check_flag_v.astype(bool)
        w_n = w_n[check_flag_v,]
        x_signal=x_signal[check_flag_v,]
        x_check_f=np.apply_along_axis(is_sorted,1,x_signal)
        
        if N>2 :
            x_signal =x_signal[x_check_f,]
            w_n      =w_n[x_check_f,]
            x_check_f=np.apply_along_axis(is_sorted2,1,x_signal)
            
        if x_signal[x_check_f,].shape[0] > 50 :
            break
        t_count -= 1
        JJ=JJ*2

    return [x_signal[x_check_f,],w_n[x_check_f,]]




'''
Data preprocessing
'''


def pre_data(Est_data):
    col_name=['ID', 'bidder_act', 'len_act', 'bidder_pos', 'bidder_state','bidder_price','ladder_norm',
              'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
    # get rid of number of bidder = = 1
    Est_data=Est_data[Est_data['num_bidder']>1]
    Est_data=Est_data[Est_data['num_bidder']<=10]
    Est_data=Est_data[Est_data['len_act']>2]

    # double check
    Est_data['real_num_bidder']= Est_data['bidder_state'].apply(lambda x: len(x))
    Est_data=Est_data[Est_data['real_num_bidder']>1]
    Est_data=Est_data[Est_data['real_num_bidder']<=10]
    # get rid of priority people
    Est_data=Est_data[Est_data['priority_people']==0]
    
    
    # normalize reservation price
    Est_data['res_norm']=Est_data['reserve_price']/Est_data['evaluation_price']
    Est_data = Est_data[np.isfinite(Est_data['res_norm'])]
    Est_data=Est_data.dropna(subset=['res_norm'])
    Est_data=Est_data[Est_data['res_norm'] >= 0.7]
    # normalize the win bid
    Est_data['win_norm']=Est_data['win_bid']/Est_data['evaluation_price']
    
    # normalize bid ladder 
    Est_data['ladder_norm']=Est_data['bid_ladder']/Est_data['evaluation_price']
    
    Est_data['bidder_price']=Est_data['bidder_price'].apply(lambda x: np.array(x) )
    Est_data['price_norm'] = Est_data['bidder_price']/Est_data['evaluation_price']

    Est_data=Est_data[Est_data['real_num_bidder']>4]
    return Est_data[col_name]
                


# def is_pos_def(Theta):
#     flag=True
#     for n in range(2,9):
#         temp_matrix= np.ones((n,n))*Theta['comm_var'] + np.eye(n)*(Theta['priv_var']+Theta['noise_var'])    
#         # check whether all the n are positive definite
#         if not np.all(LA.eigvals(temp_matrix) > 0):
#             flag=False


#     return flag