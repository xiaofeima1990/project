# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 16:28:00 2018

@author: xiaofeima

bidding functions or updating rules  

"""

import numpy as np
from numpy.linalg import inv
from scipy.stats import norm

class Update_rule:
    
    def __init__(self,para):
        self.xi_mu=para.xi_mu
        self.xi_sigma2 = para.xi_sigma2 
        self.vi_mu     = para.vi_mu
        self.vi_sigma2 = para.vi_sigma2
        self.MU        = para.MU
        self.SIGMA2    = para.SIGMA2
        self.xi_rival_mu = para.xi_rival_mu
        self.xi_rival_sigma2 = para.xi_rival_sigma2
        self.vi_rival_mu = para.xi_rival_mu
        self.vi_rival_sigma2 = para.xi_rival_sigma2
        self.N         =  para.N
        self.comm_var  = para.comm_var
        self.comm_mu  = para.comm_mu
        
    def l_bound(self,state):
        # uninformed lower bound 
        # get the info structure
        
        pos=state[1:]

        price_v=[self.T_p[x] for x in pos]

        pos     = np.asarray(pos)
        pos     = pos.reshape(pos.size,1)
        

        

        price_v = np.asarray(price_v)
        price_v = price_v.reshape(price_v.size,1)

        info_struct=np.concatenate((pos,price_v,self.xi_rival_mu,self.xi_rival_sigma2,self.vi_rival_mu,self.vi_rival_sigma2),axis=1)
        # temp[::-1].sort() sorts the array in place
        info_struct=info_struct[info_struct[:,0].argsort()[::-1]]
        
        drop_info_v=np.zeros((self.N-1,7))
        info_drop = np.zeros(self.N-1)
        
        for k in range(0, self.N-1,1):
            drop_info_v[k,:]=self.HS_system(k,info_struct,self.MU,self.SIGMA2,info_drop)
            info_drop=drop_info_v[:,0]
    
        drop_info_v=drop_info_v[drop_info_v[:,1].argsort()[::-1]]
        return drop_info_v
        
    def HS_system(self,k,info_struct,MU,Sigma,info_drop):
        
        (n_r,n_c)=info_struct.shape
        if k != 0 :
            # drop out x at 
            x_d = info_drop
            x_d = x_d[x_d>0]
            
            p_k=info_struct[-1-k, 1]
            
            
            # mu_k
            mu_k = np.append(self.vi_mu, info_struct[:n_r-k+1,4])
            
            
            
            mu_k = mu_k[0:self.N-k]
            mu_k = mu_k.reshape(mu_k.size,1)

            
            l_k  = np.ones((self.N-k,1))
            
            Gamma_k = np.append(self.vi_sigma2, info_struct[:n_r-k+1,5])
            Gamma_k = Gamma_k[0:self.N-k]
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            Delta_k =self.vi_sigma2 * np.eye(self.N)+np.ones((self.N,self.N)) * self.comm_var - np.eye(self.N) * self.comm_var  
            Delta_k=Delta_k[:,0:self.N-k].T
            
            Sigma_inv = inv(Sigma)
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:]
            
            Sigma_inv_k2 = Sigma_inv[self.N-k:,:]
            
            

            AA_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ l_k
            
            temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
            temp_diag=temp_diag.reshape(temp_diag.size,1)
            
            CC_k = 0.5*inv(Delta_k @ Sigma_inv_k1.T) @ (Gamma_k - temp_diag + 2*mu_k -2* Delta_k @ Sigma_inv @ MU)

            DD_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ (Delta_k @ (Sigma_inv_k2.T))
            
            

            

            x_drop = AA_k[-1]*p_k - np.dot( DD_k[-1,:],  x_d) - CC_k[-1]

            
            
            
            
        else:
            p_k=info_struct[-1, 1]
            
            
            
                
            # mu_k
            mu_k = np.append(self.vi_mu, info_struct[:n_r-k+1,3])
            mu_k=mu_k.reshape(mu_k.size,1)
            
            l_k  = np.ones((self.N-k,1))
            
            Gamma_k = np.append(self.vi_sigma2, info_struct[:n_r-k+1,4])
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            
            Delta_k =self.vi_sigma2*np.eye(self.N)+np.ones((self.N,self.N))*self.comm_var - np.eye(self.N)*self.comm_var  

            
            Sigma_inv = inv(Sigma)
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:]
            # Sigma_inv_k2 = Sigma_inv(N-k+1:N,:);
            
            
            AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
            
            temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
            temp_diag=temp_diag.reshape(temp_diag.size,1)
            CC_k = 0.5*inv(Delta_k @ (Sigma_inv_k1.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)
            # DD_k = inv(Delta_k*(Sigma_inv_k1.T))*(Delta_k*(Sigma_inv_k2.T))
            

            x_drop = AA_k[-1]*p_k - CC_k[-1]
        
        return np.append(x_drop,info_struct[-1-k,:])

    def real_bid(self,xi,bid,state,price_v):
        self.T_p = price_v
        
        lower_b = self.l_bound(state)
        
        #  dropout x
        x_j_lower = lower_b[:,0]
        j_N = len(x_j_lower)
        # Constat part 
        Sigma_inv = inv(self.SIGMA2);

        
        COV_xvi=np.append(self.vi_sigma2,np.ones(self.N-1)*self.comm_var)

        
        CC_i = self.vi_mu - self.MU.T @ Sigma_inv @ COV_xvi
        AA_coef =  Sigma_inv @ COV_xvi

        AA_i = AA_coef[0]
        AA_j = AA_coef[1:]
        
        x_j=np.zeros((self.N-1,1));
        for j in range(0,j_N):
            l_b = x_j_lower[j];
            u_b = -1;
            mu_j = lower_b[j,3];
            sigma_j = lower_b[j,4];
            x_j[j] = self.truc_x(mu_j,sigma_j,l_b,u_b)
            
        
        
        
        E_j = x_j.T @ AA_j
        
        
        # expectation 
        E_update= CC_i + AA_i*xi + E_j
        
        E_q=0
        
        # conditional variance var(v_i | x_i , x_j , x_q)
        Si_va=Sigma_inv; 
        part_mu=COV_xvi.T @ Si_va[1:,:].T @ self.MU[1:]
        # sigma_vi^2 , cov_xi_vi == sigma_vi^2 
        var_update = self.vi_sigma2 -AA_i*self.vi_sigma2 + (E_j+E_q -part_mu )**2

        Update_value = 0.5*var_update + E_update;
        
        
        # prepare for the winning bid expectation : take expectation on x_i x_j 
        E_const = CC_i+0.5*var_update
        
        
        
        # 4 last thing calculating the potnetial dropout signal x_j upper bound 
        # if x_j drops at the next bid
        
        # dropout x , dropout position, dropout price  x_mu x_sigma
        
        upper_b_j = self.u_bound_E(bid,state)
        
        
        # the real expected value
        try:
            Integ_part = 0;
            for s in range(0, j_N): 
        
                Integ_part = Integ_part + AA_j[s]*self.truc_x(self.MU[s],self.SIGMA2[s,s],x_j_lower[s],upper_b_j[s,0]);
            
        except Exception as e:
            print(e)
            print(x_j_lower)
            print(upper_b_j)
            print('-------------------------')
        
        E_win_revenue=Integ_part+E_const +  + AA_i*xi -self.T_p[bid]

        Pure_value = Integ_part+E_const +  + AA_i*xi 
        
        flag = int(1*(E_win_revenue>0))
        # return pure value E_win and flag
        return [Pure_value,E_win_revenue,flag]
    
    
    def u_bound_E(self,bid,state):
        pos=state[1:]
        
        price_v=[self.T_p[x] for x in pos]
        
        pos     = np.asarray(pos)
        pos     = pos.reshape(pos.size,1)
        
        price_v = np.asarray(price_v)
        price_v = price_v.reshape(price_v.size,1)
        
        
        info_struct=np.concatenate((pos,price_v,self.xi_rival_mu,self.xi_rival_sigma2,self.vi_rival_mu,self.vi_rival_sigma2),axis=1)
        # temp[::-1].sort() sorts the array in place
        info_struct=info_struct[info_struct[:,0].argsort()[::-1]]
        
        #-------------------------------------------------
        # new part: pulg in the bid price for the remainning guy
        #-------------------------------------------------
        
        bid_price= self.T_p[bid]
        
        info_struct[:,0] = bid
        info_struct[:,1] = bid_price
        
        info_drop=np.zeros(self.N-1)
        drop_info_jj = np.zeros((self.N-1,7))
        try:
            for jj in range(0, self.N-1):
                # dropout x , dropout position, dropout price  x_mu x_sigma
                drop_info_jj[jj,:]=self.HS_system(jj,info_struct,self.MU,self.SIGMA2,info_drop)
                info_drop=drop_info_jj[:,0]
            
            
            drop_info_jj=drop_info_jj[drop_info_jj[:,1].argsort()[::-1]]
            
        except Exception as e:
            print(e)
            print(price_v)
            
            
        return drop_info_jj

  
                
    
    def truc_x(self,Mu,Sigma,lower,upper):
        Sigma=Sigma**0.5
        
        a = (lower-Mu)/(Sigma)
        b = (upper-Mu)/(Sigma)
        
        if upper == -1:
            result = Mu + Sigma * norm.pdf( a)/(1-norm.pdf( a))
            # result = truncate(pd,lower,Inf);
           
        else:
            
            if lower == -1:
                result = Mu-Sigma*norm.pdf( b)/(1-norm.cdf( b))
            else:
                result = Mu+Sigma*(norm.pdf(a) - norm.pdf(b) ) /(norm.cdf(b) - norm.cdf(a)) 
            
            
        return result
        
        
    
       
        
        

class update_results:
    def __init__(self,info_dict):
        self.info_dict=info_dict
        
    @property 
    def up_val(self):
        '''
        return x i mu
        '''
        return self.info_dict['up_val']
    
    @property 
    def const(self):
        '''
        return x i mu
        '''
        return self.info_dict['const']

    @property 
    def A_i(self):
        '''
        return x i mu
        '''
        return self.info_dict['A_i']

    @property 
    def A_j(self):
        '''
        return x i mu
        '''
        return self.info_dict['A_j']

    @property 
    def j_low(self):
        '''
        return x i mu
        '''
        return self.info_dict['j_low']

    @property 
    def j_up(self):
        '''
        return x i mu
        '''
        return self.info_dict['j_up']

    @property 
    def drop_info(self):
        '''
        return x i mu
        '''
        return self.info_dict['drop_info']
    
    