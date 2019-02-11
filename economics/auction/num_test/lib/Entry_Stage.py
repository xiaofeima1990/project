# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 16:48:00 2019

@author: xiaofeima

Endogous entry choice. Here I want to generate the distribution 

"""


import numpy as np
from numpy.linalg import inv
from scipy.stats import norm
import warnings
import math,copy
from scipy.optimize import minimize
import scipy.stats as ss
from Update_rule_simu import Update_rule
from ENV import ENV
from functools import partial


class Entry_stage:
    
    def __init__(self,para,res=0):
        self.para      = para
        self.N         = para.N
        self.res       = res


    def dist_entry_bidder(self,info_flag,x_bar):
        '''
        this is used for generating endogenous entry for the number of bidders 
        1. get the entry threshold 
        2. calculate possion process
        3. prob

        '''
        ## entry threshold for uninformed bidder 
        if x_bar ==-10:
            x_bar = self.entry_threshold(self.res,info_flag)
        

        ## construct the prob for # of bidder 
    def H_prob(self,X_r,info_flag):
        mu     = self.para['comm_mu'] + self.para['beta']*np.log(self.res) + self.para['epsilon_mu ']* (1-info_flag)
        sigma2 = self.para['comm_var'] + self.para['priv_var'] + self.para['epsilon_var'] 

        return 1 - norm.cdf(X_r,mu,sigma2)
    
    def P_n(self,p_lambda,H_p,info_flag,n):
        '''
        probilitiy for the number of bidders enter into the auction
        p = (H/(1-H)**n*1/(math.factorial(n)) * (np.exp(-p_lambda*(1-H_p)) ) * (p_lambda*(1-H_p))**n 
        '''

        p = (H_p/(1-H_p)) **n * 1/(math.factorial(int(n))) * (np.exp(-p_lambda*(1-H_p))) * (p_lambda*(1-H_p))**n
        return np.log(p)
        
    def mle_func_lambda(self,p_lambda,H_p,data,info_flag=0):
        result=np.array(map(partial(self.P_n,p_lambda,H_p,info_flag),data))
        return  -np.sum(result)


    def MLE_lambda(self,X_r,data,info_flag=0):
        '''
        doing the MLE estimation for lambda
        ''' 
        H_p = self.H_prob(X_r,info_flag)
        lambda_est=minimize(self.mle_func_lambda,5,args=(H_p,data,info_flag))

        return lambda_est.x

        
    def entry_threshold(self,reserve,info_flag=0,P_lambda=5):
        '''
        calculate two constraints for entry decisions 
        1. feaible 
        2. incentive compability 
        '''

        if info_flag == 0:
            X_bar    = -0.1
            cons     = minimize(self.constraint_entry_uninfo, X_bar, method='Nelder-Mead',args=(P_lambda,reserve,self.para)) 
        else:
            X_bar    = np.array([-0.1,-0.1])
            cons     = minimize(self.constraint_entry_info, X_bar, method='Nelder-Mead',args=(P_lambda,reserve,self.para)) 


        return cons.x



    def constraint_entry_uninfo(self,X_r,P_lambda,reserve,dict_para,N_max=10):
        '''
        optimization function for uninformed case
        len(X_r) == 1 

        '''

        v_cons_1=0
        for n in range(2, N_max+1):
            Env=ENV(n,dict_para)

            # ordered index for the bidders remove
            rank_index=np.ones(n)
            # informed or not informed
            info_index_v= np.ones(n)
            i_id = 0 
            # argum ent for info_struct info_index,ord_index,res
            para=Env.info_struct(info_index_v,rank_index,reserve)
            
            pmf_poisson = ss.poisson.pmf(n,P_lambda)
            
            bid_function=Update_rule(para)
            bid_function.setup_para(i_id)
            x_s = np.ones(n)*X_r
            exp_value=bid_function.get_exp(x_s)[0]
            v_cons_1=v_cons_1+pmf_poisson*exp_value
        
        return (v_cons_1-reserve)**2


    def constraint_entry_info(self,X_r,P_lambda,reserve,dict_para,N_max=10):
        '''
        optimization function for uninformed case
        len(X_r) == 2

        '''
        v_cons_1=0
        v_cons_2=0
        v_cons_3=0

        for n in range(2, N_max+1):
            Env=ENV(n,dict_para)

            # ordered index for the bidders remove
            rank_index=np.ones(n)
            # informed or not informed
            info_index_v= np.ones(n)
            info_index_v[1]=0
            
            para=Env.info_struct(info_index_v,rank_index,reserve)
            exp_value=np.zeros(2)

            for i in range(2):
                # get uninformed bidder first 
                bid_function=Update_rule(para)
                bid_function.setup_para(i)
                x_s = np.ones(n)*X_r[0]
                x_s[1-i] = X_r[1]
                
                exp_value[i]=bid_function.get_exp(x_s)[0]
            
            pmf_poisson = ss.poisson.pmf(n,P_lambda)
            
            v_cons_1=v_cons_1+pmf_poisson*exp_value[0]
            v_cons_2=v_cons_2+pmf_poisson*exp_value[1]
            v_cons_3=v_cons_3+pmf_poisson*(exp_value[0]-exp_value[1])

        return v_cons_3**2 + (1*(v_cons_2<reserve)*v_cons_2)**2 + (1*(v_cons_1<reserve)*v_cons_1)**2