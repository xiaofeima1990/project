# -*- coding: utf-8 -*-
"""
Created on Wed Feb 06 14:28:00 2019

@author: xiaofeima

Use a new bidding function scripts to do the estimation

"""


import numpy as np
from numpy.linalg import inv
from scipy.stats import norm
import warnings
import math,copy
from scipy.optimize import minimize
import scipy.stats as ss




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
        mu_k=mu_k.reshape(mu_k.size,1)
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


    def threshold(self, p_low):
        '''
        Calculate the entry threshold for the auction given the reserve price 
        ??
        wait the modificiation for the informed case 
        ??

        '''

        ## all the rivals bidding price is known
        ## I have to re order the p_low for correct calculation 
        ## since under symmetric case, I do not need to worry about the varicne order
        
        p_k=np.sort(p_low)
        p_k=p_low.reshape(p_k.size,1)
        # mu_k
        x_drop=np.zeros(self.N)
        Sigma_inv = inv(self.SIGMA2)
        MU = self.MU
        for k in range(self.N):
            
            mu_k = np.append(self.vi_mu, self.vi_rival_mu)
            mu_k = mu_k[0:self.N-k]
            mu_k = mu_k.reshape(mu_k.size,1)
            
            l_k  = np.ones((self.N-k,1))
            
            Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
            Gamma_k = Gamma_k[0:self.N-k]
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            
            Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2)-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
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
        
        return x_drop.reshape(1,x_drop.size)


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
        
        ori_ind=ss.rankdata(p_low)
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
        return x_drop.reshape(1,x_drop.size)

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
        
        ori_ind=ss.rankdata(p_low)
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

        return x_drop[1:]


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


    def post_E_value(self,state_p_l_bound,no_flag,xi_v):
        '''
        calculate the expected value from the first "round" to last "round"

        no_flag means if there is no bid from one bidder, we do not count that bidder
        '''
        E_post=np.array([])
        E_value_list=[]
        for k in range(0,self.N): # number of "round"
            # deal with the bidding state 
            temp_state = state_p_l_bound[self.N-1 -k,: ]
            no_flag_temp = no_flag[self.N-1 -k,:]
            temp_E_value=[]            
            for i in range(0,self.N-k): # the "remaining bidder"
                # operate the bidding history
                temp_state_i = copy.deepcopy(temp_state)
                i_p=temp_state_i[i]
                temp_state_i = np.delete(temp_state_i,i)
                no_flag_temp_i = np.delete(no_flag_temp,i)

                E_value_i=self.bid_vector1(xi_v[i],temp_state_i,i_p,no_flag_temp_i,i)
                E_value_i=E_value_i.flatten()
                # save the expected highest posting expectection for that round
                if i == self.N-k-1:
                    E_post=np.append(E_post,E_value_i)
                else:
                    # save all the remaining bidders except for last one
                    temp_E_value.append(E_value_i)
            if k < self.N-1:
                E_value_list.append(temp_E_value)

        return  [E_post,E_value_list]   

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