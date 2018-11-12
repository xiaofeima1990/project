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
from Update_rule import Update_bid
from scipy.interpolate import interpn
from ENV import ENV 


para_dict={
        "comm_mu":10,
        "priv_mu":1,
        "noise_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "noise_var":0.8,
        }



class Simu:
    def __init__(self,N=3,para,T=200,rng_seed=123,dict_para=para_dict):
        self.xi_mu=para.xi_mu
        self.xi_sigma2 = para.xi_sigma2 
        self.vi_mu     = para.vi_mu
        self.vi_sigma2 = para.vi_sigma2
        self.MU        = para.MU
        self.SIGMA2    = para.SIGMA2
        self.xi_rival_mu     = para.xi_rival_mu
        self.xi_rival_sigma2 = para.xi_rival_sigma2
        self.N         = N

        self.rng       =np.random.RandomState(rng_seed)
                
        self.comm_mu   =dict_para['comm_mu']
        self.priv_mu   =dict_para['priv_mu']
        self.noise_mu  =dict_para['noise_mu']
        self.comm_var  =dict_para['comm_var']
        self.priv_var  =dict_para['priv_var']
        self.noise_var =dict_para['noise_var']
        
        self.ENV       =ENV(N,rng_seed, dict_para)
        self.Uninform_info  =ENV.Uninform()
        
        
        
    def signal_DGP(self,flag_ID=0):
        g_m = -1 + (1+1)*self.rng.rand() 
        # common value in public
        pub_mu = self.comm_mu + g_m
        
        # random reservation ratio
        # r =  0.8 + 0.1*self.rng.rand() 
        r =  0.8
        
        
        mu_x = self.comm_mu+self.priv_mu+self.epsilon_mu
        sigma_x = self.comm_var + self.priv_var+ self.epsilon_var
        
        x_signal=self.rng.normal(mu_x,sigma_x,self.N)
        
        info_index=0
        
        if info_index==1:
            mu_x = self.comm_mu+self.priv_mu
            sigma_x = self.comm_var + self.priv_var
        
            x_info=self.rng.normal(mu_x,sigma_x)
            
            info_index=self.rng.randint(3)
            x_signal[info_index]=x_info
        
        
        
        return [pub_mu,x_signal,r,info_index]
    
    
    def interp_update_rule(self,E_update_rule,T_p_old,T_p_new,xi_v_old,xi_v_new):
        # given the large bidding function result, I interp current simulation 
        # bidding function
        # possibly abbandon in the future
        N=self.N
        interp_mesh = np.array(np.meshgrid(xi_v_new, T_p_new,T_p_new,T_p_new))
        interp_points = np.rollaxis(interp_mesh, 0, 5).reshape((interp_mesh/(1+N), 1+N))
        
        
        return interpn((xi_v_old,T_p_old,T_p_old,T_p_old), E_update_rule, interp_points)
    
    
    def Data_simu(self,SS,T_end):
        # functions for simulating the bidding path given the numebr of simualted times
        
        # initilize the updating rule 
        
        Update_rule=Update_bid(self.Uninform_info)
        
        
        data_act=np.zeros((SS,T_end))
        pub_info=np.zeros((SS,T_end))
        data_state=np.zeros((SS,self.N))
        data_bid_freq=np.zeros((SS,self.N))
        data_win=np.zeros((SS,1))
        
        freq_i=np.zeros((SS,1))
        num_i = np.zeros((SS,1))
        diff_i = np.zeros((SS,1))
        
        # Active_flag=np.ones(self.N)
        flag_ID=0
        for s in range(0,SS):
            [pub_mu,x_signal, reserve]=self.signal_DGP(flag_ID)
            pub_info[s,:]=[pub_mu, reserve,self.N]
            
            price_v=[np.linspace(0.8*pub_mu,pub_mu*1.2, 30),np.linspace(1.24*pub_mu,pub_mu*1.8, 5),np.linspace(1.85*pub_mu,pub_mu*2.5,5)];
        
            State = np.zeros(self.N)
            Active= np.ones(self.N)
            
            
            for t in range(0,T_end):
                
                if t == 1: 
                    curr_bidder=np.argmax(x_signal)
                    data_act[s,t] = curr_bidder
                    State[curr_bidder]=State[curr_bidder]+1
                else:
                    
                    for i in range(0,self.N):
                        temp_state=State
                        
                        ii = temp_state[i]
                        temp_state=np.delete(temp_state,i)
                        i1 = temp_state[0]
                        i2 = temp_state[1]
                        ss_state = [ii,i1,i2]
               
                        bid = max(ss_state)+1
                        result = Update_rule.real_bid(x_signal(i),bid,ss_state,price_v)
                        
                        Active[i] = result[2]
                        
                        
                    if sum(Active) ==1:
                        index=np.nonzero(Active)
                        posting=data_act[s,t-1]
                        if index == posting:
                            data_act[s,t:] = -1
                        else:
                            curr_bidder      = index
                            data_act[s,t]    = curr_bidder
                            data_act[s,t+1:] = -1
                        
                        break
                    else :
                        if sum(Active) == 0:
                            data_act[s,t:] = -1
                            break
                        
                        
                        
                        posting=data_act[s,t-1]
                        index=np.nonzero(Active)
                        if posting in index :
                            index.reomve(posting)
                           
                       
                       
                        curr_bidder   = rng.choice(index,size=1) 
                        data_act[s,t] = curr_bidder
                        State[curr_bidder] = max(State) + 1
           
        
            # final state
            data_state[s,:]=State
            
            # calculate the high posit
            unique, counts = np.unique(data_act[s,:], return_counts=True)
            a=zip(unique,counts) 
            for ele in a:
                if ele[0] != -1:
                    data_bid_freq[s,ele[0]]=ele[1]
                else:
                    continue
                    
            # comb = list(combinations(list(range(0,self.N)), 2))
            comb=np.array(np.meshgrid(data_bid_freq[s,:], data_bid_freq[s,:])).T.reshape(-1,2)
            v=abs(comb[:,0]-comb[:,1])
            freq_i(s)=sum(v)

            
            
            # winning
            data_win[s]=para.T_p(max(State)) / (pub_mu*reserve)
            
            # high posit
            diff_i[s]=std(max(State)-State)
            
            
            # find real bidding bidders
            num_i[s]  =sum((State>0)*1)
            
            

        
        data_dict={
                'data_act':data_act,
                'pub_info':pub_info,
                'data_state':data_state,
                'data_bid_freq':data_bid_freq,
                'data_win':data_win,
                'freq_i':freq_i,
                'num_i':num_i,
                'diff_i':diff_i
                
                }
        

        return data_struct(data_dict)
    
            
class data_struct:
    def __init__(self,data_dict):
        self.data_dict=data_dict
        
    @property 
    def data_act(self):
        '''
        return x i mu
        '''
        return self.data_dict['data_act']

    @property 
    def pub_info(self):
        '''
        return x i mu
        '''
        return self.data_dict['pub_info']

    @property 
    def data_state(self):
        '''
        return x i mu
        '''
        return self.data_dict['data_state']

    @property 
    def data_bid_freq(self):
        '''
        return x i mu
        '''
        return self.data_dict['data_bid_freq']

    @property 
    def data_win(self):
        '''
        return x i mu
        '''
        return self.data_dict['data_win']

    @property 
    def freq_i(self):
        '''
        return x i mu
        '''
        return self.data_dict['freq_i']

    @property 
    def num_i(self):
        '''
        return x i mu
        '''
        return self.data_dict['num_i']
        
    
    @property 
    def diff_i(self):
        '''
        return x i mu
        '''
        return self.data_dict['diff_i']
        
        