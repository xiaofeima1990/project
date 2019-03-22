# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 16:48:00 2019

@author: xiaofeima
This is for hypothesis testing of the information asymmetry
1 use the estimated parameters to calculate X_bar and lambda 
2 lambda can be calculated by MLE 
3 compare the lambda under pi=0 and pi=1

"""
import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))

lib_path= os.path.dirname(PATH) + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Est/'


import numpy as np
import pandas as pd
from numpy.linalg import inv
from scipy.stats import norm
import warnings
import math,copy
from scipy.optimize import minimize
import scipy.stats as ss
from Update_rule_simu import Update_rule
from ENV import ENV
from Entry_Stage2 import Entry_stage
from Util import*  

if __name__ == '__main__':
    
    Est_para_dict={

        "comm_mu":0.008033,
        "beta":1.292920,
        "epsilon_mu":0,
        "comm_var":0.160956,
        "priv_var":0.001353,
        "epsilon_var":0.122577,
				
        }
    # load 
    Est_data=pd.read_hdf(data_path+'est.h5',key='test_raw')


    
    stage_1=Entry_stage(Est_para_dict)

    # uninformed case reserve price can be random 
    # lambda determines the X_bar, so just do the MLE for lambda  
    
    P_lambda  = 5.5
    max_N=10
    flag_mode=1
    flag_choice=1
    N_boot=50
    if flag_mode==0:
        if flag_choice==0:
            print("start hypothesis testing!")
            info_flag = 0
            Est_data=pre_data_stage1(Est_data,max_N,info_flag)
            ##  un_X_r = stage_1.entry_threshold(reserve,info_flag,P_lambda)
            Est_data_can=Est_data[['res_norm','real_num_bidder']]
            lambda_est = stage_1.MLE_lambda(Est_data_can,info_flag)
            print("uninfo case: first attempt lambda is {}".format(lambda_est))
        else:

            info_flag = 1
            Est_data=pre_data_stage1(Est_data,max_N,info_flag)
            # ## un_X_r = stage_1.entry_threshold(reserve,info_flag,P_lambda)
            Est_data_can=Est_data[['res_norm','real_num_bidder']]
            lambda_est = stage_1.MLE_lambda(Est_data_can,info_flag)
            print("info case: first attempt lambda is {}".format(lambda_est))
    else:
        if flag_choice==0:
            info_flag = 0
            Est_data=pre_data_stage1(Est_data,max_N,info_flag)
            Est_data_can=Est_data[['res_norm','real_num_bidder']]
            n_data=len(Est_data_can)
            np.random.seed(54321)
            for i in range(N_boot):
                Est_data_boot=Est_data_can.loc[np.random.choice(Est_data_can.index,n_data,replace=True),]
                lambda_est = stage_1.MLE_lambda(Est_data_boot,info_flag)
                print("uninfo case: first attempt lambda is {}".format(lambda_est))	
                with open('hypothesis_test' + str(info_flag) +'boot.txt', 'a+') as f:
                        f.write("{0:.12f}\n".format(lambda_est[0]))	
        else:
            info_flag = 1
            Est_data=pre_data_stage1(Est_data,max_N,info_flag)
            Est_data_can=Est_data[['res_norm','real_num_bidder']]
            n_data=len(Est_data_can)
            np.random.seed(12345)
            for i in range(N_boot):
                Est_data_boot=Est_data_can.loc[np.random.choice(Est_data_can.index,n_data,replace=True),]
                lambda_est = stage_1.MLE_lambda(Est_data_boot,info_flag)
                print("uninfo case: first attempt lambda is {}".format(lambda_est))	
                with open('hypothesis_test' + str(info_flag) +'boot.txt', 'a+') as f:
                    f.write("{0:.12f}\n".format(lambda_est[0]))	
