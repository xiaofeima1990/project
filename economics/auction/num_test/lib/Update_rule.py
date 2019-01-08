# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 16:28:00 2018

@author: xiaofeima

bidding functions or updating rules  
Now this is used for estimation. I can simultaneously estimation all the lower bounds

A little modification for the private part
I need to cite the bidder identity (rank identity)
in real_bid_calc(...,i_id)
remember the price needs to take log form

"""

import numpy as np
from numpy.linalg import inv
from scipy.stats import norm
import warnings
import math
# warnings.filterwarnings('error')


class Update_rule:
    
    def __init__(self,para,res=0):
        self.para=para
        self.N         =  para.N
        self.res = res
        self.comm_var  = para.comm_var
        self.comm_mu  = para.comm_mu

    def setup_para(self,i_id):
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


        # dimension
        #             
        self.MU              = self.MU.reshape(self.N,1)
        self.xi_rival_mu     = self.xi_rival_mu.reshape(self.N-1,1)
        self.xi_rival_sigma2 = self.xi_rival_sigma2.reshape(self.N-1,1)
        self.vi_rival_mu     = self.vi_rival_mu.reshape(self.N-1,1)
        self.vi_rival_sigma2 = self.vi_rival_sigma2.reshape(self.N-1,1)

        
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

        # temp[::-1].sort() sorts the array in place decesdening order
        info_struct=info_struct[info_struct[:,0].argsort()[::-1]]
        # get the dropout price and lower bound for private xj
        drop_info_v=self.HS_system(info_struct,self.MU,self.SIGMA2)
        
        drop_info_v=drop_info_v[drop_info_v[:,1].argsort()[::-1]]

        return drop_info_v
        
    def HS_system(self,info_struct,MU,Sigma):
        
        (n_r,n_c)=info_struct.shape
        ## all the rivals bidding price is known
        p_k=info_struct[:, 1]
        p_k=p_k.reshape(p_k.size,1)
        # mu_k
        
        mu_k = np.append(self.vi_mu, info_struct[:n_r+1,4])
        mu_k=mu_k.reshape(mu_k.size,1)
        
        l_k  = np.ones((self.N,1))
        
        Gamma_k = np.append(self.vi_sigma2, info_struct[:n_r+1,5])
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        
        
        Delta_k =np.diag(np.append(self.vi_sigma2, info_struct[:n_r+1,5])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var

        
        Sigma_inv = inv(Sigma)
        # Sigma_inv_k1 = Sigma_inv[0:self.N,:] # N-1+1 all the rest of the 

        AA_k = inv(Delta_k @ Sigma_inv.T) @ l_k
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ (Sigma_inv.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)

        

        x_drop = AA_k[1:]*p_k - CC_k[1:]
        x_drop = x_drop.reshape(x_drop.size,1)
        try:
            assert not np.prod(np.isnan(x_drop.flatten())) , 'nan occurs!'
        except Exception as e:
            print('------problem-----')
            print(e)
            print(x_drop)
            print(info_struct)
            print('MU ', MU)
            print('Sigma ', Sigma)
            print('reserve ', self.res)
            print('Gamma_k ',Gamma_k )
            print('Delta_k ',Delta_k)
            print('AA_k ', AA_k)
            print('CC_k ', CC_k)
            print('------------------')
            input('pause for check')

        return np.concatenate((x_drop,info_struct),axis=1)

    def real_info_bid(self,xi,bid,price_v):
        E_win_revenue = xi - np.log(price_v[bid])
        Pure_value    = xi
        flag = 1*(E_win_revenue>0)

        return [Pure_value,E_win_revenue,flag]


    def real_bid(self,xi,bid,state,price_v):
        self.T_p = np.log(price_v)
        ladder=np.log(price_v[-1])-np.log(price_v[-2])
        lower_b = self.l_bound(state)
        
        #  dropout x
        x_j_lower = lower_b[:,0]

        # Constat part 
        Sigma_inv = inv(self.SIGMA2)

        COV_xvi=np.append(self.vi_sigma2,np.ones(self.N-1)*self.comm_var)

        CC_i = self.vi_mu - self.MU.T @ Sigma_inv @ COV_xvi
        AA_coef =  Sigma_inv @ COV_xvi
        
        AA_i = AA_coef[0]
        AA_j = AA_coef[1:]

        # potential upper bound of the rivals
        upper_b_j = self.u_bound_E(bid,state)

        # prepare for the winning bid expectation : take expectation on x_j 
        # up + lower of the rivals
        try:
            x_j_upper=upper_b_j[:,0]
            x_j_upper=1*(x_j_upper>x_j_lower)*x_j_upper + 1*((x_j_upper <= x_j_lower)*x_j_lower + ladder*2 )
            
            E_j=sum(AA_j*self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower,x_j_upper))
        except Exception as e:
            print(e)            
            print(x_j_lower)
            print(x_j_upper)
            print(upper_b_j[:,0:2])
            print('-------------------------')

        # conditional variance var(v_i | x_i , x_j , x_q)
        Si_va=Sigma_inv
        part_mu=COV_xvi.T @ Si_va[1:,:].T @ self.MU[1:]
        # sigma_vi^2 , cov_xi_vi == sigma_vi^2 
        var_update = self.vi_sigma2 -AA_i*self.vi_sigma2 + (E_j-part_mu )**2
        
        
        # constant part 
        E_const = CC_i+0.5*var_update
        
        # total expected value
        try:
            E_win_revenue=E_j+E_const  + AA_i*xi -self.T_p[bid]
            assert not np.prod(np.iscomplex(E_win_revenue.flatten())), 'complex occurs!'
        except Exception as e:
            print('find the complex')
            print(E_win_revenue)
            print(var_update)
            print(x_j_lower)
            print(x_j_upper)
            print(E_j,E_const)
            print(AA_i,xi)
            print(bid,self.T_p[bid])

            input('wait')
        Pure_value = E_j+E_const + AA_i*xi 
        
        flag = int(1*(E_win_revenue>0))
        # return pure value E_win and flag
        return [Pure_value,E_win_revenue,flag]

    def real_bid_calc(self,bid,state,price_v,i_id):
        self.T_p = np.log(price_v)
        ladder=np.log(price_v[-1]) - np.log(price_v[-2])
        lower_b = self.l_bound(state)
        
        #  dropout x
        x_j_lower = lower_b[:,0]


        # Constat part 
        Sigma_inv = inv(self.SIGMA2)

        
        COV_xvi=np.append(self.vi_sigma2,np.ones(self.N-1)*self.comm_var)

        
        CC_i = self.vi_mu - self.MU.T @ Sigma_inv @ COV_xvi
        AA_coef =  Sigma_inv @ COV_xvi
        
        AA_i = AA_coef[0]
        AA_j = AA_coef[1:]


        # potential upper bound of the rivals
        upper_b_j = self.u_bound_E(bid,state)


        # prepare for the winning bid expectation : take expectation on x_j 
        # up + lower of the rivals
        try:
            x_j_upper=upper_b_j[:,0]
            x_j_upper=1*(x_j_upper>x_j_lower)*x_j_upper + 1*((x_j_upper <= x_j_lower)*x_j_lower + ladder )
            

            E_j=sum(AA_j*self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower,x_j_upper))
        except Exception as e:
            print(e)            
            print(x_j_lower)
            print(x_j_upper)
            print(upper_b_j[:,0:2])
            print('-------------------------')

        # conditional variance var(v_i | x_i , x_j , x_q)
        Si_va=Sigma_inv
        part_mu=COV_xvi.T @ Si_va[1:,:].T @ self.MU[1:]
        # sigma_vi^2 , cov_xi_vi == sigma_vi^2 
        var_update = self.vi_sigma2 -AA_i*self.vi_sigma2 + (E_j-part_mu )**2
        
        
        # constant part 
        E_const = CC_i+0.5*var_update
        
        # total expected value
        
        Pure_value=E_j+E_const
        bid_price =self.T_p[bid]

        return [Pure_value,bid_price,AA_i]



    def bid_vector(self,xi_v,bid,state,price_v,i_id):
        self.setup_para(i_id)

        [Pure_value,bid_price,AA_i]=self.real_bid_calc(bid,state,price_v,i_id)

        return AA_i*xi_v+Pure_value


    
    
    def u_bound_E(self,bid,state):
        
        
        #-------------------------------------------------
        # new part: pulg in the bid price for the remainning guy
        #-------------------------------------------------        
        bid_price= self.T_p[bid]
        pos     = bid*np.ones(self.N-1)
        pos     = pos.reshape(pos.size,1)
        price_v = bid_price*np.ones(self.N-1)
        price_v = price_v.reshape(price_v.size,1)

        
        info_struct=np.concatenate((pos,price_v,self.xi_rival_mu,self.xi_rival_sigma2,self.vi_rival_mu,self.vi_rival_sigma2),axis=1)
        # temp[::-1].sort() sorts the array in place
        info_struct=info_struct[info_struct[:,0].argsort()[::-1]]
        
        
        drop_info_jj = np.zeros((self.N-1,7))
        try:

            # dropout x , dropout position, dropout price  x_mu x_sigma
            drop_info_jj=self.HS_system(info_struct,self.MU,self.SIGMA2)
            
            
            drop_info_jj=drop_info_jj[drop_info_jj[:,1].argsort()[::-1]]
            
        except Exception as e:
            print(e)
            print(price_v)
            
            
        return drop_info_jj

  
                
    # this can support vectorize
    def truc_x(self,Mu,Sigma,lower,upper):
        Sigma=Sigma**0.5
        
        a = (lower-Mu)/(Sigma)
        b = (upper-Mu)/(Sigma)
        
        temp_de = norm.cdf(b) - norm.cdf(a)+10**(-8)
        temp_no = norm.pdf(a) - norm.pdf(b)
        result = Mu+Sigma*(temp_no / temp_de)


        # if sum(upper == -1:
        #     result = Mu + Sigma * norm.pdf( a)/(1-norm.pdf( a))
        #     # result = truncate(pd,lower,Inf);
           
        # else:
            
        #     if lower == -1:
        #         result = Mu-Sigma*norm.pdf(b)/(1-norm.cdf(b))
        #     else:
        #         result = Mu+Sigma*(norm.pdf(a) - norm.pdf(b) ) /(norm.cdf(b) - norm.cdf(a)) 
            
            
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
    
    