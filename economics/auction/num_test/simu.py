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
from Update_rule import Update_rule
from scipy.interpolate import interpn
from ENV import ENV 



para_dict={
        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }




class Simu:
    def __init__(self,N=3,T=200,rng_seed=123,dict_para=para_dict):


        self.rng       =np.random.RandomState(rng_seed)
                
        self.comm_mu   =dict_para['comm_mu']
        self.priv_mu   =dict_para['priv_mu']
        self.noise_mu  =dict_para['epsilon_mu']
        self.comm_var  =dict_para['comm_var']
        self.priv_var  =dict_para['priv_var']
        self.noise_var =dict_para['epsilon_var']
        self.T         =T
        self.ENV       =ENV(N, dict_para)
        

        
        
    def signal_DGP(self,N,flag_ID=0):
        g_m = -1 + (1+1)*self.rng.rand() 
        # common value in public
        pub_mu = self.comm_mu + g_m
        
        # random reservation ratio
        # r =  0.8 + 0.1*self.rng.rand() 
        r =  0.8
        
        
        mu_x = self.info_para.xi_mu
        sigma_x = self.info_para.xi_sigma2 
        
        x_signal=self.rng.normal(mu_x,sigma_x,N)
        
        info_index=0
        
        if info_index==1:
            mu_x = self.comm_mu+self.priv_mu
            sigma_x = self.comm_var + self.priv_var
        
            x_info=self.rng.normal(mu_x,sigma_x)
            
            info_index=self.rng.randint(3)
            x_signal[info_index]=x_info
        
        
        
        return [pub_mu,x_signal,r,info_index]
    
    
    def interp_update_rule(self,N,E_update_rule,T_p_old,T_p_new,xi_v_old,xi_v_new):
        # given the large bidding function result, I interp current simulation 
        # bidding function
        # possibly abbandon in the future
        
        interp_mesh = np.array(np.meshgrid(xi_v_new, T_p_new,T_p_new,T_p_new))
        interp_points = np.rollaxis(interp_mesh, 0, 5).reshape((interp_mesh/(1+N), 1+N))
        
        
        return interpn((xi_v_old,T_p_old,T_p_old,T_p_old), E_update_rule, interp_points)
    
    
    def Data_simu(self,T_end,info_flag=0):
        # functions for simulating the bidding path given the numebr of simualted times
        
        # initilize the updating rule 
        SS=self.T
        if info_flag==0:
            self.info_para  =self.ENV.Uninform()
        else:
            self.info_para  =self.ENV.Info_ID()
            
        Update_bid=Update_rule(self.info_para)
        N = self.info_para.N
        
        data_act=np.zeros((SS,T_end),dtype=int)
        pub_info=np.zeros((SS,4))
        data_state=np.zeros((SS,N))
        data_bid_freq=np.zeros((SS,N))
        data_win=np.zeros((SS,1))
        
        freq_i=np.zeros((SS,1))
        num_i = np.zeros((SS,1))
        diff_i = np.zeros((SS,1))
        
        # Active_flag=np.ones(N)
        for s in range(0,SS):
            [pub_mu,x_signal, reserve,info_index]=self.signal_DGP(N,info_flag)
            pub_info[s,:]=[pub_mu, reserve,N,info_index]
            
            price_v = np.linspace(0.8*pub_mu,pub_mu*1.2, T_end-10)
            price_v=np.append(price_v,np.linspace(1.24*pub_mu,pub_mu*1.8, 5))
            price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,5))
            
            self.T_p=price_v
            
            State = np.zeros(N)
            Active= np.ones(N)
            
            
            for t in range(0,T_end):
                
                if t == 1: 
                    curr_bidder=int(np.argmax(x_signal))
                    data_act[s,t] = curr_bidder
                    State[curr_bidder]=State[curr_bidder]+1
                else:
                    
                    for i in range(0,N):
                        temp_state=State
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)
                        i1 = int(temp_state[0])
                        i2 = int(temp_state[1])
                        ss_state = [ii,i1,i2]
               
                        bid = max(ss_state)+1
                        result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
                        
                        Active[i] = result[2]
                        
                        
                    if sum(Active) ==1:
                        index=np.nonzero(Active)[0].tolist()
                        
                        posting=data_act[s,t-1]
                        if index == posting:
                            data_act[s,t:] = int(-1)
                        else:
                            curr_bidder      = int(index[0])
                            data_act[s,t]    = int(curr_bidder)
                            data_act[s,t+1:] = int(-1)
                        
                        break
                    else :
                        if sum(Active) == 0:
                            data_act[s,t:] = int(-1)
                            break
                        
                        
                        
                        posting=data_act[s,t-1]
                        index=np.nonzero(Active)[0].tolist()
                        if posting in index :
                            index.remove(posting)
                           
                       
                       
                        curr_bidder   = self.rng.choice(index,size=1) 
                        data_act[s,t] = int(curr_bidder)
                        State[curr_bidder] = max(State) + 1
           
        
            # final state
            data_state[s,:]=State
            
            # calculate the high posit
            unique, counts = np.unique(data_act[s,:], return_counts=True)
            a=zip(unique,counts) 
            for ele in a:
                if ele[0] != -1:
                    data_bid_freq[s,int(ele[0])]=ele[1]
                else:
                    continue
                    
            # comb = list(combinations(list(range(0,N)), 2))
            comb=np.array(np.meshgrid(data_bid_freq[s,:], data_bid_freq[s,:])).T.reshape(-1,2)
            v=abs(comb[:,0]-comb[:,1])
            freq_i[s]=sum(v)

            
            
            # winning
            data_win[s]=price_v[int(max(State))] / (pub_mu*reserve)
            
            # high posit
            diff_i[s]=np.std(max(State)-State)
            
            
            # find real bidding bidders
            num_i[s]  =int(sum((State>0)*1))
            
            

        
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
    def data_win2(self):
        '''
        return x i mu
        '''
        return np.square(self.data_dict['data_win']-np.mean(self.data_dict['data_win']))

    @property 
    def freq_i(self):
        '''
        return x i mu
        '''
        return self.data_dict['freq_i']


    @property 
    def freq_i2(self):
        '''
        return x i mu
        '''
        return np.square(self.data_dict['freq_i']-np.mean(self.data_dict['freq_i']))

    @property 
    def num_i(self):
        '''
        return x i mu
        '''
        return self.data_dict['num_i']
    
    
    @property 
    def num_i2(self):
        '''
        return x i mu
        '''
        return np.square(self.data_dict['num_i']-np.mean(self.data_dict['num_i']))
        
    
    @property 
    def diff_i(self):
        '''
        return x i mu
        '''
        return self.data_dict['diff_i']
        
    @property 
    def diff_i2(self):
        '''
        return x i mu
        '''
        return np.square(self.data_dict['diff_i']-np.mean(self.data_dict['diff_i']))
                