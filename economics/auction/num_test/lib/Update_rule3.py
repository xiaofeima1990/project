# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 08:28:00 2019

@author: xiaofeima

use the new method I figured out to do the calculation
# ------------New Updation 03-26-2019---------------------------# 
lower bound: 
start from lowest bidding price 

upper bound:
start from highest bidding price 
Here I introudce three things :
1. truncated function generation process
2. lower and upper support recovered from bidding history
3. MLE estimation method


"""

import numpy as np
from numpy.linalg import inv
from scipy.stats import norm,truncnorm
import warnings
import math,copy
from scipy.optimize import minimize
import scipy.stats as ss
from numpy import linalg as LA

class Update_rule:
    
    def __init__(self,para,res=0):
        self.para=para
        self.N         =  para.N
        self.res = res
        self.comm_var  = para.comm_var
        self.comm_mu  = para.comm_mu

    def setup_para(self,i_id):
        '''
        Set up the parameters for the each bidder
        '''
        self.xi_mu        = self.para.xi_mu[i_id]
        self.xi_sigma2    = self.para.xi_sigma2[i_id] 
        self.vi_mu        = self.para.vi_mu[i_id]
        self.vi_sigma2    = self.para.vi_sigma2[i_id]
        self.MU           = self.para.MU[i_id]
        self.SIGMA2       = self.para.SIGMA2[i_id]
        self.xi_rival_mu  = self.para.xi_rival_mu[i_id]
        self.xi_rival_sigma2 = self.para.xi_rival_sigma2[i_id]
        self.vi_rival_mu     = self.para.vi_rival_mu[i_id]
        self.vi_rival_sigma2 = self.para.vi_rival_sigma2[i_id]   
        self.cov_istar       = self.para.cov_istar[i_id]

        # dimension
        #             
        self.MU              = self.MU.reshape(self.N,1)
        self.xi_rival_mu     = self.xi_rival_mu.reshape(self.N-1,1)
        self.xi_rival_sigma2 = self.xi_rival_sigma2.reshape(self.N-1,1)
        self.vi_rival_mu     = self.vi_rival_mu.reshape(self.N-1,1)
        self.vi_rival_sigma2 = self.vi_rival_sigma2.reshape(self.N-1,1)
        self.cov_istar       = self.cov_istar.reshape(self.N,1) 


    def threshold_simple(self, p_low):
        '''
        calculate the entry threshold for the x, 
        so that we can select proper x for numerical integration
        This is simplified version which does not involve the loop
        '''

        p_k=p_low.reshape(p_low.size,1)
        x_drop=np.zeros(self.N)

        # MU and SIGMA2
        Sigma_inv = inv(self.SIGMA2)
        MU = self.MU.reshape(self.MU.size,1)
        
        # mu_k
        mu_k = np.append(self.vi_mu, self.vi_rival_mu)
        mu_k = mu_k.reshape(mu_k.size,1)
        # l_k
        l_k  = np.ones((self.N,1))
        # gamma_k
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        # Delta_k
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2)-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        Delta_k=Delta_k.T

        # constant part and coefficient matrix
        AA_k = inv(Delta_k @ Sigma_inv.T) @ l_k
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ (Sigma_inv.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)

        x_drop = AA_k*np.log(p_k) - CC_k

        return x_drop


    def get_lower_p_bound(self, x_s):
        '''
        from X to P, use x to calculate the Price
        '''

        # signal
        x_s = x_s.reshape(x_s.size,1)
        # prespecify the mu Gamma, Delta
        mu_k = np.append(self.vi_mu, self.vi_rival_mu)
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
        Delta_k =self.vi_sigma2 * np.eye(self.N)+np.ones((self.N,self.N)) * self.comm_var - np.eye(self.N) * self.comm_var  
        x_drop=np.array([])
        drop_price_l_bound=np.array([])
        for k in range(0,self.N):
            # mu 
            mu_k = mu_k[0:self.N-k]
            mu_k=mu_k.reshape(mu_k.size,1)

            # gamma
            Gamma_k = Gamma_k[0:self.N-k]
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            # Delta
            Delta_k=Delta_k[:,0:self.N-k].T
            
            # sigma_inv
            Sigma_inv = inv(self.SIGMA2)        
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:]
            
            # the main 
            AA_k = Delta_k @ Sigma_inv_k1.T  # coefficient matrix
            temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
            temp_diag=temp_diag.reshape(temp_diag.size,1)
            CC_k = 0.5*  (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@self.MU)
                        
            if k>0:
                Sigma_inv_k2 = Sigma_inv[self.N-k:,:] 
                DD_k = (Delta_k @ (Sigma_inv_k2.T))
                drop_price= AA_k @ x_s +DD_k @ x_drop +CC_k
            else:
                drop_price= AA_k @ x_s  + CC_k

            x_drop=np.append(x_s[self.N-1 - k],x_drop)
            drop_price_l_bound=np.append(drop_price[-1],drop_price_l_bound)
        return drop_price_l_bound
            

    def l_bound_xj_1(self,p_low,p_i,k,low_support):
        '''
        lower bound for private signal from bidding price
        k : the order of the bidding price the higher the small
            k=N-1 winner k=0 first to drop
        '''

        low_support=low_support.reshape(self.N-1,1)
        # get the rank order and reorder the bidding sequence
        ord_ind2=np.argsort(p_low)[::-1]
        
        ori_ind=ss.rankdata(p_low,method='ordinal')
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        p_k=p_low[ord_ind2]
        # construct the bidding price vector
        p_k=np.append(p_i,p_k)
        p_k=p_k.reshape(p_k.size,1)

        # prepare for iteration
        x_drop=np.zeros([self.N,1])
        Sigma_inv = inv(self.SIGMA2)
        MU = self.MU
        x_d=np.array([])

        # k=0 the first to drop 
        # mu
        mu_k = np.append(self.vi_mu, self.vi_rival_mu[ord_ind2])
        mu_k = mu_k[0:self.N-k]
        mu_k=mu_k.reshape(mu_k.size,1)
        # l
        l_k  = np.ones((self.N-k,1))
        # Gamma
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])
        Gamma_k = Gamma_k[0:self.N-k]
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        # Delta
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        Delta_k=Delta_k[:,0:self.N-k].T
        # Sigma^-1 k1 
        Sigma_inv_k1 = Sigma_inv[0:self.N-k,:] # N-1+1 all the rest of the 
        # coefficient matrix for remaining bidders
        AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
        # constant
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ Sigma_inv_k1.T) @ (Gamma_k - temp_diag + 2*mu_k -2* Delta_k @ Sigma_inv @ MU)

        # k>0 plug in the lower support 
        if k>0:
            Sigma_inv_k2 = Sigma_inv[self.N-k:,:]
            # coefficient matrix for dropped bidders
            DD_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ (Delta_k @ (Sigma_inv_k2.T))

            x_drop[:self.N-k] = AA_k[-1] * (p_k[:self.N-k]) - DD_k @ low_support[:k] - CC_k        
        else:
            DD_k = np.zeros([1,1])
            x_drop[:self.N-k] = AA_k[-1] *p_k[:self.N-k] - CC_k
        
        return x_drop[0]

    def u_bound_xj_1(self, p_up,k,high_support):
        '''
        lower bound for private signal from bidding price
        k : the order of the bidding price the higher the small
            k=N-1 winner k=0 first to drop

        I do not need the order or something in this sense
        '''

        k=self.N-1
        # p_up should have size equal to  N
        p_k=p_up*np.ones([self.N-k,1])
        high_support=high_support.reshape(self.N-1,1)
        # prepare for iteration
        x_drop=np.zeros([self.N-k,1])
        Sigma_inv = inv(self.SIGMA2)
        MU = self.MU

        # mu
        mu_k = np.append(self.vi_mu, self.vi_rival_mu)
        mu_k = mu_k[0:self.N-k]
        mu_k=mu_k.reshape(mu_k.size,1)
        # l
        l_k  = np.ones((self.N-k,1))
        # Gamma
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
        Gamma_k = Gamma_k[0:self.N-k]
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        # Delta
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2)-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        Delta_k=Delta_k[:,0:self.N-k].T
        # Sigma^-1 k1 
        Sigma_inv_k1 = Sigma_inv[0:self.N-k,:] # N-1+1 all the rest of the 
        # coefficient matrix for remaining bidders
        AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
        # constant
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ Sigma_inv_k1.T) @ (Gamma_k - temp_diag + 2*mu_k -2* Delta_k @ Sigma_inv @ MU)

        # k=0 the first to get information
        if k>0:
            Sigma_inv_k2 = Sigma_inv[self.N-k:,:]
            # coefficient matrix for dropped bidders
            DD_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ (Delta_k @ (Sigma_inv_k2.T))

            x_drop = AA_k[-1] * (p_k) - DD_k @ high_support[self.N-1-k:] - CC_k        
        else:
            DD_k = np.zeros([1,1])
            x_drop[:self.N-k] = AA_k[-1] *p_k[:self.N-k] - CC_k

        return x_drop[0]

    def l_bound_xj_0(self,p_low):
        '''
        upper bound for private signal from the bidding price
        ''' 
        pre_MU    =self.MU.flatten()
        pre_SIGMA2=np.diag(self.SIGMA2)
        p_low=p_low.flatten()
        x_drop=np.zeros(self.N)
        # get the order info from the bidding activity p_low
        # highest to lowest 
        ord_ind2=np.argsort(p_low)[::-1]

        ori_ind=ss.rankdata(p_low,method='ordinal')
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        p_k=p_low[ord_ind2]
        p_k=p_k.reshape(p_k.size,1)

        # MU and SIGMA2
        post_SIGMA2=np.append(pre_SIGMA2[0],pre_SIGMA2[1:][ord_ind2])
        post_SIGMA2=np.ones([self.N,self.N])*self.comm_var + np.diag(post_SIGMA2)-np.eye(self.N)*self.comm_var
        Sigma_inv = inv(post_SIGMA2)
        MU = np.append(pre_MU[0],pre_MU[1:][ord_ind2])
        MU = MU.reshape(MU.size,1)

        # mu_k
        mu_k = np.append(self.vi_mu, self.vi_rival_mu[ord_ind2])
        mu_k=mu_k.reshape(mu_k.size,1)
        # l_k
        l_k  = np.ones((self.N,1))
        # Gamma_k
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        # Delta_k
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        # inverse of coefficient matrix 
        AA_k = inv(Delta_k @ Sigma_inv.T) @ l_k
        # constant
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ (Sigma_inv.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)

        x_drop = AA_k[1:]*p_k - CC_k[1:]
        # recover the order of the sequence 
        x_drop=x_drop[::-1][ori_ind]

        return x_drop

    def u_bound_xj_0(self,p_up,p_low):
        '''
        upper bound for private signal from the bidding price
        ''' 
        pre_MU    =self.MU.flatten()
        pre_SIGMA2=np.diag(self.SIGMA2)
        p_low=p_low.flatten()
        x_drop=np.zeros(self.N)
        # get the order info from the bidding activity p_low
        # highest to lowest 
        ord_ind2=np.argsort(p_low)[::-1]
        
        ori_ind=ss.rankdata(p_low,method="ordinal")
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        
        p_k=p_up.reshape(p_up.size,1)

        # MU and SIGMA2
        post_SIGMA2=np.append(pre_SIGMA2[0],pre_SIGMA2[1:][ord_ind2])
        post_SIGMA2=np.ones([self.N,self.N])*self.comm_var + np.diag(post_SIGMA2)-np.eye(self.N)*self.comm_var
        Sigma_inv = inv(post_SIGMA2)
        MU = np.append(pre_MU[0],pre_MU[1:][ord_ind2])
        MU = MU.reshape(MU.size,1)

        # mu_k
        mu_k = np.append(self.vi_mu, self.vi_rival_mu[ord_ind2])
        mu_k=mu_k.reshape(mu_k.size,1)
        # l_k
        l_k  = np.ones((self.N,1))
        # Gamma_k
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        # Delta_k
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        # inverse of coefficient matrix 
        AA_k = inv(Delta_k @ Sigma_inv.T) @ l_k
        # constant
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ (Sigma_inv.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)

        x_drop = AA_k[1:]*p_k - CC_k[1:]
        # recover the order of the sequence 
        #x_drop=np.append(x_drop[0],x_drop[1:][::-1][ori_ind])
        x_drop=x_drop[::-1][ori_ind]
        return x_drop

    def real_bid_calc_new(self,ord_id):
        '''
        pivotal bidding function
        '''
        
        # inverse matrix
        Sigma_inv = inv(self.SIGMA2)
        
        # Covariance part
        # COV_xvi=np.append(self.vi_sigma2,np.ones(self.N-1)*self.comm_var)
        COV_xvi=self.cov_istar
        # constant
        CC_i = self.vi_mu - self.MU.T @ Sigma_inv @ COV_xvi
        # coefficient matrix
        AA_coef =  Sigma_inv @ COV_xvi
        AA_i = AA_coef[ord_id]
        AA_j = np.delete(AA_coef,ord_id)
        # variance part 
        var_update = self.vi_sigma2 -COV_xvi.T @  Sigma_inv @  COV_xvi

        # gross constant part 
        E_const = CC_i+0.5*var_update

        return [E_const.flatten(),AA_i.flatten(),AA_j.flatten()]



    def support_x(self,state_p_l_bound,bid_post_log,threshold,no_flag,ladder):
        '''
        get the lower and upper bound support of xi from all the moment inequalities 
        most important function
        '''
        low_support  = np.zeros(self.N)
        high_support = np.zeros(self.N)

        # lower support
        for k in range(0,self.N): # number of "round"
            temp_state = state_p_l_bound[self.N-1 -k,: ]
            temp_state_i = copy.deepcopy(temp_state)
            temp_state_i = np.delete(temp_state_i,self.N-1 -k)
            i_p=bid_post_log[self.N-1 -k]
            temp_low=np.delete(low_support,k)
            low_support[k]=self.l_bound_xj_1(temp_state_i,i_p,k,temp_low)
            if k==0 and low_support[k]<threshold[0]:
                low_support[k]=threshold[0]

        # higher support 
        p_up= max(bid_post_log)
        high_support[-1] = low_support[-1]+2*ladder
        
        if self.N >2:
            high_support[-2] = low_support[-2]+ladder/10000
            N_start=2
        else:
            N_start=1
            
        for kk in range(N_start,self.N):

            temp_high=np.delete(high_support,self.N-1 -k)
            high_support[self.N-1-kk]=self.u_bound_xj_1(p_up,kk,temp_high)
        
        return [low_support.reshape(low_support.size,1),high_support.reshape(high_support.size,1)]


    def bid_vector1(self,xi_v,state_p,no_flag,p_up,ladder,i_id):
        '''
        xi_v vectors for xi private signal
        state_p normalized bidding price under the coresponding bidding history
        i_id the ordered identiy of the bidders
        '''

        # doe not need to count the x signal criterion
        self.setup_para(i_id)
        # Pure_value, bid_price, AA_i -> only in log form
        # I have to go back to normal price
        [E_const,AA_i,AA_j]=self.real_bid_calc_new(i_id)
        # ladder=np.log(price_v[-1]) - np.log(price_v[-2])
        xi_v = xi_v.flatten()
        # state_p is just the only dropout part N-1 length
        x_j_lower = self.l_bound_xj_0(state_p)
        x_j_lower=x_j_lower.flatten()

        i_p_v=np.log(np.exp(p_up)+2*ladder)*np.ones(state_p.size)
        x_j_upper = self.u_bound_xj_0(i_p_v,state_p)
        x_j_upper = x_j_upper.flatten()
        E_j = self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower,x_j_upper) * AA_j
        E_j = np.sum(E_j.flatten())

        exp_value= AA_i*xi_v + E_j + E_const 
        return exp_value.flatten()


    def post_E_value(self,state_p_l_bound,no_flag,ladder,xi_v):
        '''
        calculate the expected value from the first "round" to last "round"
        '''
        E_post=np.zeros(self.N)
        E_value_list=[]
        for k in range(0,self.N): # number of "round"
            # deal with the bidding state 
            temp_state = state_p_l_bound[self.N-1 -k,: ]
            no_flag_temp = no_flag[self.N-1 -k,:]
            temp_E_value=[]
            # own expected evalution for k 
            temp_state_k = copy.deepcopy(temp_state)
            p_up=max(temp_state_k)
            temp_state_k = np.delete(temp_state_k,self.N-k-1)
            no_flag_temp_k = np.delete(no_flag_temp,self.N-k-1)
            E_post[k]=self.bid_vector1(xi_v[k],temp_state_k,no_flag_temp_k,p_up,ladder,k)

            for i in range(0,2): # the "remaining bidder" highest and second higest
                temp_state_i = copy.deepcopy(temp_state)
                p_up=max(temp_state_i)
                temp_state_i = np.delete(temp_state_i,i)
                no_flag_temp_i = np.delete(no_flag_temp,i)
                E_value_i=self.bid_vector1(xi_v[self.N-1-i],temp_state_i,no_flag_temp_i,p_up,ladder,self.N-1-i)
                E_value_i=E_value_i.flatten()
                # save the expected highest posting expectection for that round
                if i != self.N-k-1:
                    # highest to lowest 
                    temp_E_value.append(E_value_i)
            if k < self.N-1:
                # from first dropout bidder to last one
                E_value_list.append(temp_E_value)

        return  [E_post,E_value_list]   


    def cal_E_i(self,x_v,w_v,low_support,high_support,i_id):
        # use cal_bid to get Ai Aj and const part 
        [E_const,AA_i,AA_j]=self.real_bid_calc_new(i_id)

        is_sorted = lambda a: np.all(a[i_id] <= a[i_id:])
        is_sorted2 = lambda a: np.all(a[i_id] > a[:i_id])
        x_check_f=np.apply_along_axis(is_sorted,0,x_v)
        x_check_f2=np.apply_along_axis(is_sorted2,0,x_v)
        # select the candidate X 
        # x_flag1      = 1*(x_v[i_id,:] >= low_support)
        # x_flag2      = 1*(x_v[i_id,:] <= high_support)
        # check_flag_v1=x_flag1*x_flag2
        check_flag_v1=x_check_f*x_check_f2*1
        

        E_xi_v= AA_i*x_v[i_id,:]+ AA_j@np.delete(x_v,i_id,axis=0)
        E_xi_v=E_xi_v*w_v*check_flag_v1
        no_E  =np.sum(E_xi_v) # mean is fine
        de_prob= np.sum(w_v)  # mean is fine 
        E_X_cond=no_E/de_prob + E_const

        return E_X_cond


    def MLE_X_trunc(self,low_support,high_support,threshold,x2nd,x_v,w_v):
        '''
        I do not know this MLE est
        I just realized that I can genreate the conditional chain rule to calculate
        the MLE (Because I calculate the probability!!!)
        '''
        self.setup_para(0)

        low_support  = low_support.reshape(self.N,1)
        high_support = high_support.reshape(self.N,1)
        low_support[-2]=low_support[-2]-0.05
        high_support[-2]=high_support[-2]+0.05
        x_flag1      = x_v >= low_support
        x_flag2      = x_v <= high_support 

        check_flag_v1=np.prod(x_flag1, axis=0)
        check_flag_v2=np.prod(x_flag2, axis=0)
        check_flag_v1=check_flag_v1*check_flag_v2
        
        nominator     = np.sum(check_flag_v1*w_v)
        denominator   = np.sum(w_v)
        mu=self.MU[-2]
        sigma=self.SIGMA2[-2,-2]**0.5

        density_2nd  = truncnorm.pdf((x2nd-mu)/sigma,(threshold[-2]-mu)/sigma,10)
        prob_1st = 1 - truncnorm.cdf((low_support[-1]-mu)/sigma,(threshold[-1]-mu)/sigma,10)

        with np.errstate(divide='raise'):
            try:
                log_Prob      = density_2nd + prob_1st+ np.log(nominator)-np.log(denominator)
            except Exception as e:
                print('-----------------------------------------------')
                print('0 in log at {} bidders with {} reserve price'.format(self.N,threshold[0]))
                print(low_support.flatten())
                print(high_support.flatten())
                print("density_2d: {0:.4}\t| prob_1st: {0:.4}\t| nominator: {0:.4}\t| denominator: {0:.4}\t| ".format(density_2nd,prob_1st,nominator,denominator))

                log_Prob = np.nan


        log_Prob = np.log(nominator)-np.log(denominator) + np.log(density_2nd) + np.log(prob_1st)

        return log_Prob

    def MLE_X_new(self,low_support,high_support,threshold,x2nd):
        '''
        I just realized that I can genreate the conditional chain rule to calculate
        the MLE (Because I calculate the probability!!!)
        '''
        self.setup_para(0)
        mu=self.MU[-2]
        sigma=self.SIGMA2[-2,-2]**0.5

        low_support  = low_support.reshape(self.N,1)
        high_support = high_support.reshape(self.N,1)

        density_2nd  = truncnorm.pdf((x2nd-mu)/sigma,(threshold[-2]-mu)/sigma,10)
        prob_1st     = 1 - truncnorm.cdf((low_support[-1]-mu)/sigma,(threshold[-1]-mu)/sigma,10)
        with np.errstate(divide='raise'):
            try:
                log_Prob      = np.log(density_2nd) + np.log(prob_1st)
            except Exception as e:
                print('-----------------------------------------------')
                print('0 in log at {} bidders with {} reserve price'.format(self.N,threshold[0]))
                print(low_support.flatten())
                print(high_support.flatten())
                print("density_2d: {} | prob_1st: {}".format(density_2nd[0],prob_1st[0]))

                log_Prob = np.nan
                return log_Prob


        
        if self.N>2:
            for i in range(self.N-2):
                temp_low  =low_support[i+1:]
                temp_high =high_support[i+1:]

                temp_low  =np.append(threshold[i],temp_low)
                temp_high =np.append(10,temp_high)

                [x_v,U_v,w_v]=self.GHK_simulator(i,temp_low,temp_high,2)
                # last column is what we need
                #
                x_flag1      = x_v[0] >= low_support[i]
                x_flag2      = x_v[0] <= high_support[i]
                check_flag_v1 = x_flag1*x_flag2*1
                # calculate the prob 
                nominator     = np.sum(check_flag_v1*w_v)
                denominator   = np.sum(w_v)
                with np.errstate(divide='raise'):
                    try:
                        
                        log_Prob      = log_Prob + np.log(nominator)-np.log(denominator)
                    except Exception as e:
                        print('-----------------------------------------------')
                        print(e)
                        print('0 in log at {} bidders with {} reserve price for bidder {}'.format(self.N,threshold[0],i))
                        print(low_support.flatten())
                        print(high_support.flatten())
                        print("density_2d: {} \t| prob_1st: {} \t| nominator: {} \t| denominator: {} \t| ".format(density_2nd[0],prob_1st[0],nominator,denominator))

                        log_Prob = np.nan


        return log_Prob


    def MLE_X_new2(self,low_support,high_support,threshold,x2nd):
        '''
        In Karl's suggestion, conditional each Omgea_i, I can get conditional distribution for 
        each bidder i. Then I can calculate the probability that xi is under the lower and upper 
        bound
        Prob_xi( xi_low < Xi < xi_up |Omega_it)
        ignore the second highest bid first 
        '''
        self.setup_para(0)
        mu=self.MU[-2]
        sigma=self.SIGMA2[-2,-2]**0.5

        low_support  = low_support.reshape(self.N,1)
        high_support = high_support.reshape(self.N,1)


        # the higest winning private signal prob
        temp_low  =np.delete(low_support,self.N-1)
        temp_high =np.delete(high_support,self.N-1)

        temp_low  =np.append(threshold[self.N-1],temp_low)
        temp_high =np.append(10,temp_high)        

        [x_v ,w_v]=self.GHK_simulator(self.N-1,temp_low,temp_high,2)

        x_flag1      = x_v[0] >= low_support[self.N-1]
        x_flag2      = x_v[0] <= high_support[self.N-1]
        check_flag_v1 = x_flag1 * x_flag2*1
        prob_1st     = np.mean(check_flag_v1)

        with np.errstate(divide='raise'):
            try:
                log_Prob      = np.log(prob_1st)
            except Exception as e:
                print('-----------------------------------------------')
                print('0 in log at {} bidders with {} reserve price'.format(self.N,threshold[0]))
                print(low_support.flatten())
                print(high_support.flatten())
                print("density_2d: {} ".format(prob_1st[0]))

                log_Prob = np.nan
                return log_Prob


        
        if self.N>2:
            for i in range(self.N-2):
                temp_low  =np.delete(low_support,i)
                temp_high =np.delete(high_support,i) 

                temp_low  =np.append(threshold[i],temp_low)
                temp_high =np.append(10,temp_high)

                [x_v ,w_v]=self.GHK_simulator(i,temp_low,temp_high,2)
                # last column is what we need
                #
                x_flag1      = x_v[0] >= low_support[i]
                x_flag2      = x_v[0] <= high_support[i]
                check_flag_v1 = x_flag1 * x_flag2*1
                # calculate the prob is that possible? 
                #  
                Prob_temp     = np.mean(check_flag_v1) 

                with np.errstate(divide='raise'):
                    try:
                        
                        log_Prob      = log_Prob + np.log(Prob_temp)
                    except Exception as e:
                        print('-----------------------------------------------')
                        print(e)
                        print('0 in log at {} bidders with {} reserve price for bidder {}'.format(self.N,threshold[0],i))
                        print(low_support.flatten())
                        print(high_support.flatten())
                        print("prob_1st: {} \t| nominator: {} \t ".format(prob_1st,Prob_temp))

                        log_Prob = np.nan


        return log_Prob

        
    def norm_generator(self,c,d):

        Phi_c=norm.cdf(c) 
        Phi_d=norm.cdf(d)
        # standard normal
        U_v=np.random.uniform(Phi_c,Phi_d)

        return norm.ppf(U_v)

    def GHK_simulator(self,i_id,low_bound,up_bound,mode_flag=0,S=300):
        '''
        applying GHK method to generate the multivariate truncated normal distribution
        wrong modify
        '''
        self.setup_para(i_id)
        np.random.seed(114499)
 
        SS=S + (self.N)*150 
        # Cholesky factorization the Sigma

        down_ch_sigma=LA.cholesky(self.SIGMA2)
        MU=self.MU
        b = np.ones(self.N)*100 if mode_flag == 0 else  up_bound.flatten()
        a = np.ones(self.N)*(-100) if mode_flag == 1 else low_bound.flatten()


        w_a=np.zeros([self.N,SS])
        w_b=np.zeros([self.N,SS])
        w_v=np.ones([1,SS])
        U_rand_v = np.zeros([self.N,SS])
        # generate the draws recursively. It is not easy to do
        # first draw u1 from N(0,1; (a1-mu1)/s11, (b1-mu1)/s11)
        # pins down the c and d 
        c_1 = (a[0]-MU[0])/down_ch_sigma[0,0] *np.ones(SS)
        d_1 = (b[0]-MU[0])/down_ch_sigma[0,0] *np.ones(SS)

        U_rand_v[0,:] =  self.norm_generator(c_1,d_1)

        # transform to xi 

        for i in range (0, self.N):
            temp_mu=MU[i]*np.ones(SS)
            for j in range(0,i):
                temp_mu += down_ch_sigma[i,j]*U_rand_v[j,:]
            c_temp = (a[i] - temp_mu)/down_ch_sigma[i,i]
            d_temp = (b[i] - temp_mu)/down_ch_sigma[i,i]

            U_rand_v[i,:] =  self.norm_generator(c_temp,d_temp)
            
            w_b =  norm.cdf((b[i]-temp_mu)/down_ch_sigma[i,i])
            w_a =  norm.cdf((a[i]-temp_mu)/down_ch_sigma[i,i])
            #if np.abs(a[i]-b[i])/b[i] > 0.01:
            w_v *= (w_b-w_a)
        # x_v 
        x_v = MU+down_ch_sigma@U_rand_v

        return [x_v,w_v]



    '''
    HS replication
    '''

    def get_HS_drop_p(self, x_s):
        '''
        use HS system of equations to recover the price. we know the private signal
        '''



        # signal
        x_s = x_s.reshape(x_s.size,1)
        # info_struct=np.concatenate((self.xi_rival_mu,self.xi_rival_sigma2,self.vi_rival_mu,self.vi_rival_sigma2),axis=1)
                
        x_drop=np.array([])
        drop_price_v=[]
        drop_price_round=[]
        for k in range(0,self.N):
            # mu 
            mu_k = np.append(self.vi_mu, self.vi_rival_mu)
            mu_k = mu_k[0:self.N-k]
            mu_k=mu_k.reshape(mu_k.size,1)
            # l
            l_k  = np.ones((self.N-k,1))
            # gamma
            Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
            Gamma_k = Gamma_k[0:self.N-k]
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            # Delta
            Delta_k =self.vi_sigma2 * np.eye(self.N)+np.ones((self.N,self.N)) * self.comm_var - np.eye(self.N) * self.comm_var  
            Delta_k=Delta_k[:,0:self.N-k].T
            
            # sigma_inv
            Sigma_inv = inv(self.SIGMA2)        
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:]
            

            # the main 
            # AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
            temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
            temp_diag=temp_diag.reshape(temp_diag.size,1)
            CC_k = 0.5*  (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@self.MU)
                        
            if k>0:
                Sigma_inv_k2 = Sigma_inv[self.N-k:,:] 
                DD_k = (Delta_k @ (Sigma_inv_k2.T))
                drop_price= np.exp(x_s[:self.N - k] +DD_k @ x_drop +CC_k)
            else:
                drop_price= np.exp(x_s  + CC_k)

            x_drop=np.append(x_s[self.N-1 - k],x_drop)
            x_drop=x_drop.reshape(x_drop.size,1)
            drop_price=drop_price.flatten()
            drop_price_round.append(drop_price[0:-1].tolist())
            drop_price_v=np.append(drop_price_v,drop_price[-1])
        drop_price_round.pop()    
        return [drop_price_v, drop_price_round]


    def truc_x(self,Mu,Sigma,lower,upper):
        '''
        calculate the truncated moment 
        '''

        Sigma=Sigma**0.5
        
        a = (lower-Mu)/(Sigma)
        b = (upper-Mu)/(Sigma)
        temp_de = norm.cdf(b) - norm.cdf(a)+10**(-20)
        temp_no = norm.pdf(a) - norm.pdf(b)
        result = Mu+Sigma*(temp_no / temp_de)
        flag=1*(np.abs(b-a) <10**(-5))

        result =(1-flag) * result + flag * upper
        
        return result 

    def bound(self, p_low):
        '''
        may dropout
        '''
        # still I have to calculate the signal recurisively
        ## all the rivals bidding price is known
        ## but first of all, I have to reorder the "dropout price" from second to last (ignore the first)
        ## the function who invoke the bound already define the i_id
        p_low=p_low.flatten()
        pre_MU    =self.MU.flatten()
        pre_SIGMA2=np.diag(self.SIGMA2)

        # Reorder p_k from second to last 
        ord_ind1=np.argsort(p_low[1:])
        ord_ind2=np.argsort(p_low[1:])[::-1]

        ori_ind=ss.rankdata(p_low[1:])
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        p_k=np.append(p_low[0],p_low[1:][ord_ind2])
        p_k=p_k.reshape(p_k.size,1)

        # MU and SIGMA2
        post_SIGMA2=np.append(pre_SIGMA2[0],pre_SIGMA2[1:][ord_ind2])
        post_SIGMA2=np.ones([self.N,self.N])*self.comm_var + np.diag(post_SIGMA2)-np.eye(self.N)*self.comm_var
        Sigma_inv = inv(post_SIGMA2)
        MU = np.append(pre_MU[0],pre_MU[1:][ord_ind2])
        MU = MU.reshape(MU.size,1)

        # mu_k
        x_drop=np.zeros(self.N)

        # vi xi
        for k in range(self.N):
             
            mu_k = np.append(self.vi_mu, self.vi_rival_mu[ord_ind2])
            mu_k = mu_k[0:self.N-k]
            mu_k=mu_k.reshape(mu_k.size,1)
            
            l_k  = np.ones((self.N-k,1))
            
            Gamma_k = np.append(self.vi_sigma2 , self.vi_rival_sigma2[ord_ind2])
            Gamma_k = Gamma_k[0:self.N-k]
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            
            Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
            Delta_k=Delta_k[:,0:self.N-k].T
            
            
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:] # N-1+1 all the rest of the 


            AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
            temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
            temp_diag=temp_diag.reshape(temp_diag.size,1)
            
            CC_k = 0.5*inv(Delta_k @ Sigma_inv_k1.T) @ (Gamma_k - temp_diag + 2*mu_k -2* Delta_k @ Sigma_inv @ MU)

            if k>0:
                Sigma_inv_k2 = Sigma_inv[self.N-k:,:]
                DD_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ (Delta_k @ (Sigma_inv_k2.T))
                x_d = x_drop[self.N-k:]
            else:
                DD_k = np.zeros([1,1])
                x_d = 0
            x_drop[self.N-k-1] = AA_k[-1]*np.log(p_k[self.N-k-1]) - np.dot( DD_k[-1,:],  x_d) - CC_k[-1]
        
        x_drop=np.append(x_drop[0],x_drop[1:][::-1][ori_ind])
        return x_drop.reshape(1,x_drop.size)