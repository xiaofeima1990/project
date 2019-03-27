# -*- coding: utf-8 -*-
'''
Created on Thu Mar 26 19:18:00 2019

@author: xiaofeima

using GHK method to generate the truncated multivariate normal random vectors 


'''

import numpy as np
from numpy.linalg import inv
from scipy.stats import norm,truncnorm
import warnings
import math,copy
from scipy.optimize import minimize
import scipy.stats as ss
from numpy import linalg as LA

class GHK:
    
    def __init__(self,para,res=0):
        self.para=para
        self.N            =  para['N']
        self.MU           =  para['MU']
        self.SIGMA2       =  para['SIGMA2']


    def norm_generator(self,c,d):

        Phi_c=norm.cdf(c) 
        Phi_d=norm.cdf(d)
        # standard normal
        U_v=np.random.uniform(Phi_c,Phi_d)

        return norm.ppf(U_v)

    def GHK_simulator(self,low_bound,up_bound,mode_flag=0,rng=114499,S=1000):
        '''
        applying GHK method to generate the multivariate truncated normal distribution
        wrong modify
        '''
        np.random.seed(rng)
 
        SS=S + (self.N)*500 
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
