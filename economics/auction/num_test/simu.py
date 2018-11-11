# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 13:29:54 2018

@author: mgxgl
This is for the simulation part 
There exist two part, first simulate a large space for updating rule and set it 
as default.
then each time when the price path chagnes, I use interpolate method to calculate 
sub space for update rule which hopefully could acceralate the calculation speed

 

"""

import numpy as np


para_dict={
        "comm_mu":10,
        "priv_mu":1,
        "noise_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "noise_var":0.8,
        }



class Simu:
    def __init__(self,para,T=200,rng_seed=123,dict_para=para_dict):
        self.xi_mu=para.xi_mu
        self.xi_sigma2 = para.xi_sigma2 
        self.vi_mu     = para.vi_mu
        self.vi_sigma2 = para.vi_sigma2
        self.MU        = para.MU
        self.SIGMA2    = para.SIGMA2
        self.xi_rival_mu = para.xi_rival_mu
        self.xi_rival_sigma2 = para.xi_rival_sigma2
        self.N         =  self.N

        self.rng      =np.random.RandomState(rng_seed)
        
        
        self.comm_mu  =dict_para['comm_mu']
        self.priv_mu  =dict_para['priv_mu']
        self.noise_mu =dict_para['noise_mu']
        self.comm_var =dict_para['comm_var']
        self.priv_var =dict_para['priv_var']
        self.noise_var=dict_para['noise_var']
        
        
    def signal_DGP(self,flag_ID=0):
        g_m = -1 + (1+1)*self.rng.rand() 
        # common value in public
        pub_mu = self.comm_mu + g_m
        
        # random reservation ratio
        r =  0.8 + 0.1*self.rng.rand() 
        
        
        
        mu_x = self.comm_mu+self.priv_mu+self.epsilon_mu
        sigma_x = self.comm_var + self.priv_var+ self.epsilon_var
        
        x_signal=self.rng.normal(mu_x,sigma_x,self.N)
        
        info_index=0
        
        if flag_ID==1:
            mu_x = self.comm_mu+self.priv_mu
            sigma_x = self.comm_var + self.priv_var
        
            x_info=self.rng.normal(mu_x,sigma_x)
            
            info_index=self.rng.randint(3)
            x_signal[info_index]=x_info
        
        
        
        return [pub_mu,x_signal,r,info_index]
    
    
    def interp_update_rule(self,):
        pass
    
    
    def Data_simu(self):
        pass
    
    
            
        