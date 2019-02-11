# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 16:48:00 2019

@author: xiaofeima
This is for hypothesis testing of the information asymmetry

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
from Entry_Stage import Entry_stage
from Util import*  

if __name__ == '__main__':
    
    Est_para_dict={

        "comm_mu":0.005,
        "beta":0.96,
        "epsilon_mu":0,
        "comm_var":0.021,
        "priv_var":0.01,
        "epsilon_var":0.091,
        }
    # load 
    Est_data=pd.read_hdf(data_path+'est.h5',key='test_raw')

    Est_data=pre_data(Est_data)


    reserve = 0.8
    stage_1=Entry_stage(Est_para_dict,reserve)

    # uninformed case 
    info_flag = 0
    P_lambda  = 5
    un_X_r = stage_1.entry_threshold(reserve,info_flag,P_lambda)
    
    lambda_est = stage_1.MLE_lambda(un_X_r,Est_data['num_bidder'],info_flag)
