# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 12:34:00 2018

@author: xiaofeima
Numerical Test 

This script is about Environemnt Setup:
1. info structure
2. Number of Bidders

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





class ENV:
    def __init__(self, N,rng_seed=123, dict_para=para_dict):
        self.comm_mu  =dict_para['comm_mu']
        self.priv_mu  =dict_para['priv_mu']
        self.noise_mu =dict_para['noise_mu']
        self.comm_var =dict_para['comm_var']
        self.priv_var =dict_para['priv_var']
        self.noise_var=dict_para['noise_var']
        self.N=N
        self.rng=np.random.RandomState(12345)
        self.uninfo={}
        self.info_Id={}
        
        
    def Uninform(self):
        self.uninfo['xi_mu']     =  self.comm_mu+self.priv_mu + self.noise_mu
        self.uninfo['xi_sigma2'] =  self.comm_var+self.priv_var + self.noise_var
        self.uninfo['vi_mu']     =  self.comm_mu+self.priv_mu 
        self.uninfo['vi_sigma2'] =  self.comm_var+self.priv_var
        self.uninfo['N']         =  self.N
        self.uninfo['xi_rival_mu'] = (self.comm_mu+self.priv_mu + self.noise_mu) * np.ones((self.N-1,1))
        self.uninfo['xi_rival_sigma2'] = (self.comm_var+self.priv_var + self.noise_var) * np.ones((self.N-1,1))
        temp_matrix= np.ones((self.N,self.N))*self.comm_var - np.eye(self.N)*self.comm_var              
        self.uninfo['COV_i']       = np.concatenate((np.diag(self.uninfo['vi_sigma2']*np.ones(self.N)) + temp_matrix ), axis=1)
        self.uninfo['SiGMA2']      = self.uninfo['xi_sigma2']*np.ones((self.N,self.N)) + temp_matrix
        self.uninfo['MU']          = (self.comm_mu+self.priv_mu + self.noise_mu)*np.ones((self.N,1))
        return Info_result(self.uninfo)
        
    def Info_ID(self):
        self.info_Id['xi_mu']     =  self.comm_mu+self.priv_mu + self.noise_mu
        self.info_Id['xi_sigma2'] =  self.comm_var+self.priv_var + self.noise_var
        self.info_Id['vi_mu']     =  self.comm_mu+self.priv_mu 
        self.info_Id['vi_sigma2'] =  self.comm_var+self.priv_var
        self.info_Id['x_info_mu'] = self.comm_mu+self.priv_mu 
        self.info_Id['x_info_sigma2'] = self.comm_var+self.priv_var
        self.info_Id['N']         =  self.N
        temp_N2=(self.comm_mu+self.priv_mu + self.noise_mu) * np.ones((self.N-2,1))
        self.info_Id['xi_rival_mu'] = np.concatenate(((self.comm_mu+self.priv_mu)*np.ones(1,1) , temp_N2), axis=0)
        temp_N2=(self.comm_var+self.priv_var + self.noise_var) * np.ones((self.N-2,1))
        self.info_Id['xi_rival_sigma2'] = np.concatenate(((self.comm_var+self.priv_var)*np.ones(1,1) , temp_N2), axis=0)
        temp_matrix= np.ones((self.N,self.N))*self.comm_var - np.eye(self.N)*self.comm_var              
        self.info_Id['COV_i']       = np.concatenate((np.diag(self.info_Id['vi_sigma2']*np.ones(self.N)) + temp_matrix ), axis=1)
        self.info_Id['SiGMA2']      = self.info_Id['xi_sigma2']*np.ones((self.N,self.N)) + temp_matrix
        self.info_Id['MU']          = (self.comm_mu+self.priv_mu + self.noise_mu)*np.ones((self.N,1))
        return Info_result(self.info_Id)
    
    
    
    
    
class Info_result(object):
    def __init__(self,info_dict):
        '''
        mesure the distance include
        1. miles
        2. kilometers
        3. meters
        4. feet
        distance_measure={
          'miles':, 
          'kilometers':,
          'meters':,
          'feet',
        
        }
        
        '''
        self.info_dict=info_dict
    @property 
    def xi_mu(self):
        '''
        return x i mu
        '''
        return self.info_dict['xi_mu']

    @property 
    def xi_sigma2(self):
        '''
        return x i sigma square
        '''
        return self.info_dict['xi_sigma2']
        
    @property 
    def xi_mu(self):
        '''
        return x i mu
        '''
        return self.info_dict['xi_mu']
    @property 
    def vi_sigma2(self):
        '''
        return v i simga squre
        '''
        return self.info_dict['vi_sigma2']
    
    @property 
    def x_info_mu(self):
        '''
        return x i mu
        '''
        return self.info_dict['x_info_mu']
    @property 
    def x_info_mu(self):
        '''
        return v i simga squre
        '''
        return self.info_dict['x_info_sigma2']
        
    @property 
    def N(self):
        '''
        return number of bidder
        '''
        return self.info_dict['N']

    @property 
    def xi_rival_mu(self):
        '''
        return x i's  rival mu 
        '''
        return self.info_dict['xi_rival_mu']

    @property 
    def xi_rival_sigma2(self):
        '''
        return  x i's  rival sigma square 
        '''
        return self.info_dict['xi_rival_sigma2']

    @property 
    def COV_i(self):
        '''
        return Sigma i 
        '''
        return self.info_dict['COV_i']

    @property 
    def SiGMA2(self):
        '''
        return big SIGMA
        '''
        return self.info_dict['SiGMA2']

    @property 
    def MU(self):
        '''
        return mu for 
        '''
        return self.info_dict['MU']




    