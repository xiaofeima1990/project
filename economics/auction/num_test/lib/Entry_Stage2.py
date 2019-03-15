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
        H_p = self.H_prob(info_flag,(X_r,reserve))
        if len(N_vector)>1:
            prob_N = np.array(map(partial(self.P_n,p_lambda,H_p,info_flag),N_vector))
        else:
            prob_N = self.P_n(p_lambda,H_p,info_flag,N_vector)
        
        return np.exp(prob_N)
 
    ## construct the prob for # of bidder 
    def H_prob(self,info_flag,arg_data):
        X_r,log_reserve=arg_data
        mu     = self.para['comm_mu'] + self.para['beta']*log_reserve + self.para['epsilon_mu']* (1-info_flag)
        sigma2 = self.para['comm_var'] + self.para['priv_var'] + self.para['epsilon_var'] 

        return 1 - norm.cdf(X_r,mu,sigma2)
    
    def P_n(self,p_lambda,info_flag,arg_data):
        '''
        probilitiy for the number of bidders enter into the auction
        p = (H/(1-H)**n*1/(math.factorial(n)) * (np.exp(-p_lambda*(1-H_p)) ) * (p_lambda*(1-H_p))**n 
        '''
        H_p1,H_p2,n=arg_data
        n=int(n)
        if info_flag==0:
            p = (H_p1/(1-H_p1)) **n * 1/(math.factorial(n)) * (np.exp(-p_lambda*H_p1)) * (p_lambda*(1-H_p1))**n
        else:
            p = (H_p1/(1-H_p1)) **(n-1) * 1/(math.factorial(n-1)) *H_p2 * (np.exp(-p_lambda*H_p1)) * (p_lambda*(1-H_p1))**(n-1)
        return np.log(p)
        
    def mle_func_lambda(self,p_lambda,data,info_flag=0):
        '''
        given the lambda, calculate the X_r 
        given the X_r calculate the H_p
        given the H_p and data, calculate the likelihood of lambda 
        '''
        # X_r_v = np.array(list(map(partial(self.entry_threshold,info_flag,p_lambda),data['res_norm'])))
        if info_flag==0:
            [coef_sum,var_sum]=self.get_coef_uninfo(info_flag,p_lambda)
            X_r_v = np.array(list(map(partial(self.entry_uninfo_simple,p_lambda,coef_sum,var_sum),np.log(data['res_norm']))))
            X_r_v = X_r_v.reshape(X_r_v.size,1)
            X_r_v =np.tile(X_r_v,(1,2))
        else:
            [coef_sum1,coef_sum2,var_sum]=self.get_coef_info(info_flag,p_lambda)
            X_r_v = np.array(list(map(partial(self.min_info_entry,p_lambda,coef_sum1,coef_sum2,var_sum),np.log(data['res_norm']))))

        
        H_p_v1 = np.array(list(map(partial(self.H_prob,0),zip(X_r_v[:,0],np.log(data['res_norm'])))))
        H_p_v1=H_p_v1.flatten()
        H_p_v2= np.array(list(map(partial(self.H_prob,info_flag),zip(X_r_v[:,info_flag],np.log(data['res_norm'])))))
        H_p_v2=H_p_v2.flatten()

            

        result=np.array(list(map(partial(self.P_n,p_lambda,info_flag),zip(H_p_v1,H_p_v2,data['real_num_bidder']))))
        print("current candidate lambda is  {}".format(p_lambda))
        output_list=[]
        output_list= output_list + p_lambda.tolist()+np.min(X_r_v,0).tolist()+np.max(X_r_v,0).tolist()        
        with open('hypothesis_test' + str(info_flag) +'.txt', 'a+') as f:
            for ele in output_list:
                f.write("%f\t" % ele)
            
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
    def min_info_entry(self,P_lambda,coef_sum1,coef_sum2,var_sum,log_reserve,N_max=10):
        X_bar    = np.array([log_reserve,log_reserve])
        cons     = minimize(self.entry_info_simple, X_bar, method='Nelder-Mead',args=(P_lambda,log_reserve,coef_sum1,coef_sum2,var_sum,N_max)) 
        return cons.x



    def entry_uninfo_simple(self,P_lambda,coef_sum,var_part,log_reserve,N_max=10):
        '''
        simplified version of computing the entry threshold under uninformed case
        '''
        info_flag=0
        Mu_constant=self.get_MU_part(info_flag,P_lambda,log_reserve)
        X_bar=(log_reserve-Mu_constant-var_part)/coef_sum
        return X_bar

    def entry_info_simple(self,X_bar,P_lambda,log_reserve,coef_sum1,coef_sum2,var_part,N_max=10):
        '''
        simplified version of computing the entry threshold under informed case
        '''
        info_flag=0
        Mu_constant=self.get_MU_part(info_flag,P_lambda,log_reserve)
        equ1= X_bar[0]*coef_sum1 + X_bar[1]*coef_sum2 - (log_reserve-Mu_constant-var_part)
        equ2= X_bar[0]*coef_sum1 + X_bar[1]*coef_sum2 + (Mu_constant+var_part) - X_bar[1]
        
        return equ1**2 + equ2**2

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
            v_cons_1=v_cons_1+pmf_poisson*np.log(exp_value)
        
        return (v_cons_1-np.log(reserve))**2


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

    def get_coef_uninfo(self,info_flag,p_lambda,N_max=10):
        # set up the variance and mean 
        # construct the coefficient matrix
        # in asymmtric case, the second guy is the informed bidder
        coef_sum=0
        var_sum=0
        for N in range(2,N_max+1):
            pmf_poisson = ss.poisson.pmf(N,p_lambda)
            # setup the parameters
            Sigma2= self.para['comm_var']*np.ones([N,N]) + (self.para['priv_var']+self.para['epsilon_var']) * np.eye(N)
            
            Cov_1 = self.para['comm_var']*np.ones([N,1])
            Cov_1[0] = Cov_1[0] + self.para['priv_var'] 

            coeff_Matrix = np.ones([1,N]) @ inv(Sigma2) @ Cov_1 

            coef_sum += coeff_Matrix*pmf_poisson

            # symmetric case is simple 
            variance_part =  (self.para['comm_var']+self.para['priv_var']) - Cov_1.T @ inv(Sigma2) @ Cov_1
            var_sum += variance_part*0.5*pmf_poisson


        return [coef_sum,var_sum]


    def get_coef_info(self,info_flag,p_lambda,N_max=10):
        # set up the variance and mean 
        # construct the coefficient matrix
        # in asymmtric case, the second guy is the informed bidder
        coef_sum1=0
        coef_sum2=0
        var_sum=0
        for N in range(2,N_max+1):
            pmf_poisson = ss.poisson.pmf(N,p_lambda)
            # setup the parameters
            Sigma2      = self.para['comm_var']*np.ones([N,N]) + (self.para['priv_var']+self.para['epsilon_var']) * np.eye(N)
            Sigma2[1,1] = self.para['comm_var'] + self.para['priv_var']
            Cov_1       = self.para['comm_var']*np.ones([N,1])
            Cov_1[0]    = Cov_1[0] + self.para['priv_var'] 

            coeff_Matrix = inv(Sigma2)@ Cov_1 
            coeff_info=coeff_Matrix[1]
            coeff_uninfo=np.delete(coeff_Matrix,1)


            coef_sum1 += sum(coeff_uninfo)*pmf_poisson
            coef_sum2 += coeff_info*pmf_poisson
            # symmetric case is simple 
            variance_part =  (self.para['comm_var']+self.para['priv_var']) - Cov_1.T @ inv(Sigma2) @ Cov_1
            var_sum += variance_part*0.5*pmf_poisson


        return [coef_sum1,coef_sum2,var_sum]
    def get_MU_part(self,info_flag,p_lambda,reserve):
        Mu_part_sum=0
        for N in range(2,10+1):
            Mu    = (self.para['comm_mu'] + self.para['epsilon_mu']+ self.para['beta']*reserve)*np.ones(N)
            mu    = self.para['comm_mu'] + self.para['beta']*reserve

            Sigma2= self.para['comm_var']*np.ones([N,N]) + (self.para['priv_var']+self.para['epsilon_var']) * np.eye(N)
            Sigma2[1,1] = self.para['comm_var'] + self.para['priv_var']+self.para['epsilon_var']*(1-info_flag)
            Cov_1 = self.para['comm_var']*np.ones([N,1])
            Cov_1[0] = Cov_1[0] + self.para['priv_var'] 

            Mu_part = mu - Mu.T @ inv(Sigma2)@ Cov_1
            pmf_poisson = ss.poisson.pmf(N,p_lambda)

            Mu_part_sum += Mu_part*pmf_poisson

        return Mu_part_sum
