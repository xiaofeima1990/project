# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 08:28:00 2019

@author: xiaofeima

use the new method I figured out to do the calculation

lower bound: 
start from lowest bidding price 

upper bound
start from highest bidding price 

use the range of support to get trucated moment / truncated normal

calculate the moment inequality ? OR do MLE for trucated normal

(In the new Algorithm I do not even need the threshold)

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
        self.xi_mu        =self.para.xi_mu[i_id]
        self.xi_sigma2    = self.para.xi_sigma2[i_id] 
        self.vi_mu        = self.para.vi_mu[i_id]
        self.vi_sigma2    = self.para.vi_sigma2[i_id]
        self.MU           = self.para.MU[i_id]
        self.SIGMA2       = self.para.SIGMA2[i_id]
        self.xi_rival_mu  = self.para.xi_rival_mu[i_id]
        self.xi_rival_sigma2 = self.para.xi_rival_sigma2[i_id]
        self.vi_rival_mu     = self.para.vi_rival_mu[i_id]
        self.vi_rival_sigma2 = self.para.vi_rival_sigma2[i_id]   
        self.cov_istar       =self.para.cov_istar[i_id]

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
            

    def l_bound_xj(self, p_low):
        '''
        lower bound for private signal from bidding price
        '''
        # still I have to calculate the signal recurisively
        # partial finished the order issues
        ## all the rivals bidding price is known

        # get the order info from the bidding activity p_low
        # highest to lowest
        ord_ind2=np.argsort(p_low)[::-1]
        
        ori_ind=ss.rankdata(p_low,method='ordinal')
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        p_k=p_low[ord_ind2]
        p_k=p_k.reshape(p_k.size,1)

        # prepare for iteration
        x_drop=np.zeros(self.N-1)
        Sigma_inv = inv(self.SIGMA2)
        MU = self.MU
        x_d=np.array([])
        for k in range(self.N-1):
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

            
            if k>0:
                Sigma_inv_k2 = Sigma_inv[self.N-k:,:]
                # coefficient matrix for dropped bidders
                DD_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ (Delta_k @ (Sigma_inv_k2.T))
                x_drop[(self.N-1)-k-1] = AA_k[-1]*(p_k[(self.N-1)-k-1]) - np.dot( DD_k[-1,:],  x_d) - CC_k[-1]        
            else:
                DD_k = np.zeros([1,1])
                x_drop[(self.N-1)-k-1] = AA_k[-1]*(p_k[(self.N-1)-k-1]) - CC_k[-1]

            x_d = np.append(x_drop[(self.N-1)-k-1],x_d)

        x_drop=x_drop[::-1][ori_ind]
        return [x_drop.reshape(1,x_drop.size),ord_ind2,ori_ind]
 
    def u_bound_xj(self,p_up,p_low):
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

        x_drop = AA_k*p_k - CC_k
        # recover the order of the sequence 
        x_drop=np.append(x_drop[0],x_drop[1:][::-1][ori_ind])

        return [x_drop[1:],ord_ind2,ori_ind]


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


    def bid_vector1(self,xi_v,state_p,i_p,no_flag,i_id):
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
        # state_p is just the rival part N-1 length
        # lower bound 
        x_j_lower = self.l_bound_xj(state_p)
        # upper bound
        i_p_v=i_p*np.ones(state_p.size+1)
        x_j_upper = self.u_bound_xj(i_p_v,state_p)
        # The learning effect
        E_j = self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower,x_j_upper) * AA_j
        E_j = np.sum(E_j.flatten() * (1-no_flag) )
        # updated expected value
        exp_value= AA_i*xi_v + E_j + E_const 
        return np.exp(exp_value)

    def low_x_recover(self,state_p_log,i_p_log,no_flag,ladder,i_id,low_support):
        '''
        given the previous bidding history, we can use bidder i's current bidding 
        price to recover bidder i's lower bound 
        '''

        self.setup_para(i_id)
        # Pure_value, bid_price, AA_i -> only in log form
        # I have to go back to normal price
        [E_const,AA_i,AA_j]=self.real_bid_calc_new(i_id)

        [x_j_lower,ord_ind2,ori_ind] = self.l_bound_xj(state_p_log)
        x_j_lower = x_j_lower.flatten()
        x_j_lower = x_j_lower[ord_ind2]
        low_support = low_support[::-1]
        # update for lower support derived from last 
        x_j_lower[self.N-1-i_id:] = low_support[self.N-1-i_id:]
        x_j_lower = x_j_lower[::-1][ori_ind]
        # upper bound
        i_p_v=np.log(np.exp(i_p_log)+ladder)*np.ones(state_p_log.size+1)
        [x_j_upper,ord_ind2,ori_ind] = self.u_bound_xj(i_p_v,state_p_log)
        x_j_upper = x_j_upper.flatten()
        # The learning effect
        E_j = self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower,x_j_upper) * AA_j
        E_j = np.sum(E_j.flatten() * (1-no_flag) )

        # 
        xi_low = (i_p_log - E_j - E_const)/AA_i 
        return xi_low


    def upper_x_recover(self,state_p_log,p_up,no_flag,ladder,i_id,low_support,upper_support):
        '''
        given the bidding history and upper price, we recover the upper bound of the private 
        signal
        '''

        self.setup_para(i_id)
        # Pure_value, bid_price, AA_i -> only in log form
        # I have to go back to normal price
        [E_const,AA_i,AA_j]=self.real_bid_calc_new(i_id)

        # X_j is from highest to lowest
        # update for lower support derived from last loop
        [x_j_lower,ord_ind2,ori_ind] = self.l_bound_xj(state_p_log)
        x_j_lower = x_j_lower.flatten()
        x_j_lower = low_support[::-1].flatten()
        x_j_lower = x_j_lower[::-1][ori_ind]
        # upper bound
        i_p_v=np.log(np.exp(p_up)+ladder)*np.ones(state_p_log.size+1)
        [x_j_upper,ord_ind2,ori_ind] = self.u_bound_xj(i_p_v,state_p_log)
        # reorder from highest to lowest 
        x_j_upper = x_j_upper.flatten()
        x_j_upper = x_j_upper[ord_ind2]
        # replace/update for upper support derived from last loop
        upper_support=upper_support[::-1]  
        x_j_upper[:self.N-1-i_id]= upper_support[:self.N-1-i_id]
        x_j_upper = x_j_upper[::-1][ori_ind]
        

        # The learning effect
        E_j = self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower,x_j_upper) * AA_j
        E_j = np.sum(E_j.flatten())

        # 
        xi_up = (np.log(np.exp(p_up) + ladder)- E_j - E_const)/AA_i 
        return xi_up

    def support_x(self,state_p_l_bound,bid_post_log,no_flag,ladder):
        '''
        get the lower and upper bound support of xi from all the moment inequalities 
        most important function
        '''
        low_support  = np.zeros(self.N)
        high_support = np.zeros(self.N)

        # lower support
        for k in range(0,self.N): # number of "round"
            temp_state = state_p_l_bound[self.N-1 -k,: ]
            no_flag_temp = no_flag[self.N-1 -k,:]
            temp_state_i = copy.deepcopy(temp_state)
            temp_state_i = np.delete(temp_state_i,self.N-1 -k)
            no_flag_temp_i = np.delete(no_flag_temp,self.N-1 -k)
            i_p=bid_post_log[self.N-1 -k]
            temp_low=np.delete(low_support,k)
            low_support[k]=self.low_x_recover(temp_state_i,i_p,no_flag_temp_i,ladder,k,temp_low)

        # higher support 
        p_up= max(bid_post_log)
        high_support[-1] = np.log(10)
        if self.N >2:
            high_support[-2] = low_support[-2]+ladder/10000
            N_start=self.N-2-1
        else:
            N_start=self.N-1-1
        for kk in range(N_start,-1,-1):
            temp_state   = state_p_l_bound[self.N-1-kk,:]
            no_flag_temp = no_flag[self.N-1- kk,:]
            temp_state_i = copy.deepcopy(temp_state)
            temp_state_i   = np.delete(temp_state_i,self.N-1-kk)
            no_flag_temp_i = np.delete(no_flag_temp,self.N-1-kk)
            temp_low = np.delete(low_support,kk)
            temp_upp = np.delete(high_support,kk)
            high_support[kk]=self.upper_x_recover(temp_state_i,p_up,no_flag_temp_i,ladder,kk,temp_low,temp_upp)
        
        return [low_support.reshape(low_support.size,1),high_support.reshape(high_support.size,1)]


    def prob_X_trunc(self,low_support,high_support,threshold):
        '''
        highly incorrect!!!
        '''
        self.setup_para(0)

        SIGMA2   =self.SIGMA2
    
        # use scipy to comput the square root of Sigma
        [D,V]=LA.eig(SIGMA2)
        D_root = D**0.5
        inv_D  =  D_root**(-1)
        Sigma_inv = V @ np.diag(inv_D) @ LA.inv(V)
        Sigma_inv=Sigma_inv.real
        a=Sigma_inv@( threshold.reshape([self.N,1]) - self.MU.reshape([self.N,1]) )
        b=10*np.ones([self.N,1]) 
        
        
        prob_up   = truncnorm.cdf(high_support,a,b)
        prob_down = truncnorm.cdf(low_support,a,b)

        prob      = np.log(prob_up - prob_down)

        return np.sum(prob)
        



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