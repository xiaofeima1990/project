# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 16:28:00 2018

@author: xiaofeima

bidding functions or updating rules  

"""

class Update_bid:
    
    def __init__(self,para,price_v,re_price,Pub_value):
        self.xi_mu=para.xi_mu
        self.xi_sigma2 = para.xi_sigma2 
        self.vi_mu     =para.vi_mu
        self.vi_sigma2 =para.vi_sigma2
        self.MU        = para.MU
        self.SIGMA2    = para.SIGMA2
        self.N         =  self.N
        self.T_p = price_v
        self.Pub_value=Pub_value
        
    def l_bound(self,bid,state):
        
        # get the info structure
        
        pos=state[1:]
        
        Info_rival=[pos_v; P_v; xx_mu; xx_sigma;vv_mu; vv_sigma]';