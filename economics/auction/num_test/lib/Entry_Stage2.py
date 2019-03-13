# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 16:48:00 2019

@author: xiaofeima

Endogous entry choice. Here I want to generate the distribution 
X_r is affected by the lambda, we can not calcuate the X_r separately


"""


import numpy as np
from numpy.linalg import inv
from scipy.stats import norm
import warnings
import math,copy,time,datetime
from scipy.optimize import minimize
import scipy.stats as ss
from Update_rule_simu import Update_rule
from ENV import ENV
from functools import partial


class Entry_stage:
    
    def __init__(self,para,res=0):
        self.para      = para
        self.res       = res 



    def dist_entry_bidder(self,info_flag,p_lambda,reserve,N_vector):
        '''
        this is used for generating endogenous entry for the number of bidders 
        1. get the entry threshold 
        2. calculate possion process
        3. prob

        '''
        X_r = self.entry_threshold(info_flag,p_lambda, reserve) 
        
        H_p = self.H_prob(X_r,reserve,info_flag)
        if len(N_vector)>1:
            prob_N = np.array(map(partial(self.P_n,p_lambda,H_p,info_flag),N_vector))
        else:
            prob_N = self.P_n(p_lambda,H_p,info_flag,N_vector)
        
        return np.exp(prob_N)
 
    ## construct the prob for # of bidder 
    def H_prob(self,X_r,reserve,info_flag):
        mu     = self.para['comm_mu'] + self.para['beta']*np.log(reserve) + self.para['epsilon_mu']* (1-info_flag)
        sigma2 = self.para['comm_var'] + self.para['priv_var'] + self.para['epsilon_var'] 

        return 1 - norm.cdf(X_r,mu,sigma2)
    
    def P_n(self,p_lambda,H_p,info_flag,n):
        '''
        probilitiy for the number of bidders enter into the auction
        p = (H/(1-H)**n*1/(math.factorial(n)) * (np.exp(-p_lambda*(1-H_p)) ) * (p_lambda*(1-H_p))**n 
        '''
        n=int(n)
        if info_flag==0:
            p = (H_p/(1-H_p)) **n * 1/(math.factorial(n)) * (np.exp(-p_lambda*(1-H_p))) * (p_lambda*(1-H_p))**n
        else:
            p = (H_p/(1-H_p)) **(n-1) * 1/(math.factorial(n-1)) *H_p * (np.exp(-p_lambda*(1-H_p))) * (p_lambda*(1-H_p))**(n-1)
        return np.log(p)
        
    def mle_func_lambda(self,p_lambda,data,info_flag=0):
        '''
        given the lambda, calculate the X_r 
        given the X_r calculate the H_p
        given the H_p and data, calculate the likelihood of lambda 
        '''
        X_r_v = np.array(list(map(partial(self.entry_threshold,info_flag,p_lambda),data['res_norm'])))

        H_p_v = self.H_prob(X_r_v,data['res_norm'],info_flag)


        result=np.array(list(map(partial(self.P_n,p_lambda,H_p_v,info_flag),data['real_num_bidder'])))
        print("current candidate lambda is  {}".format(p_lambda))

        with open('hypothesis_test' + str(info_flag) +'.txt', 'a+') as f:
            f.write("%f\t" % p_lambda)
            f.write("%f\t" % min(X_r_v))
            f.write("%f\t" % max(X_r_v))
            
            f.write("{0:.12f}\n".format(-np.sum(result)))

        return  -np.sum(result)

 
    def MLE_lambda(self,data,info_flag=0):
        '''
        doing the MLE estimation for lambda
        info_flag = 0 uninformed case, 
                  = 1 informed case
        This is main function for calcuating the lambda 
 
        ''' 
        now = datetime.datetime.now()
        start_time=time.time()
        print("start time at "+str(now.strftime("%Y-%m-%d %H:%M")))
        lambda_est=minimize(self.mle_func_lambda,5,args=(data,info_flag))
        now = datetime.datetime.now()
        end_time=time.time()
        print("end time at "+str(now.strftime("%Y-%m-%d %H:%M")))
        print("time spend : %f minutes "%((end_time-start_time)/60) )
        print(lambda_est)
        return lambda_est.x




    def entry_threshold(self,info_flag,P_lambda,reserve):
        '''
        calculate two constraints for entry decisions 
        1. feaible 
        2. incentive compability 
        '''

        if info_flag == 0:
            X_bar    = np.log(reserve)
            cons     = minimize(self.constraint_entry_uninfo, X_bar, method='Nelder-Mead',args=(P_lambda,reserve,self.para)) 
        else:
            X_bar    = np.array([np.log(reserve),np.log(reserve)])
            cons     = minimize(self.constraint_entry_info, X_bar, method='Nelder-Mead',args=(P_lambda,reserve,self.para)) 


        return cons.x



    def constraint_entry_uninfo(self,X_r,P_lambda,reserve,dict_para,N_max=10):
        '''
        optimization function for uninformed case
        len(X_r) == 1 
        claculate the n=2 ~ max N 

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
        optimization function for informed case
        len(X_r) == 1 
        claculate the n=2 ~ max N 

        '''
        v_cons_1=0
        for n in range(2, N_max+1):
            Env=ENV(n,dict_para)

            # ordered index for the bidders remove
            rank_index=np.ones(n)
            # informed fix the second bidder as informed bidder
            info_index_v= np.ones(n)
            info_index_v[1]=0
            i_id = 0 
            # argum ent for info_struct info_index,ord_index,res
            para=Env.info_struct(info_index_v,rank_index,reserve)
            
            pmf_poisson = ss.poisson.pmf(n,P_lambda)
            
            bid_function=Update_rule(para)
            bid_function.setup_para(i_id)
            x_s = np.ones(n)*X_r[0]
            x_s[1] = X_r[1]
            exp_value=bid_function.get_exp(x_s)[0]
            v_cons_1=v_cons_1+pmf_poisson*exp_value
        
        return (v_cons_1-reserve)**2
