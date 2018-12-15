# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 13:29:54 2018

@author: mgxgl
This is for the simulation part 
new updated version:
    - fixed the number of bidders, there are exactly number of bidders attending the acution
    - add minium bidding ladder
    - modify the info structure
    - simplify the code
 

"""

import numpy as np
from Update_rule import Update_rule
from scipy.interpolate import interpn
from ENV import ENV 
import copy


para_dict={
        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }




class Simu:
    def __init__(self,rng_seed=123,dict_para=para_dict):


        self.rng       =np.random.RandomState(rng_seed)
                
        self.comm_mu   =dict_para['comm_mu']
        self.priv_mu   =dict_para['priv_mu']
        self.noise_mu  =dict_para['epsilon_mu']
        self.comm_var  =dict_para['comm_var']
        self.priv_var  =dict_para['priv_var']
        self.noise_var =dict_para['epsilon_var']
        self.dict_para =dict_para

        
        

        
        
    def signal_DGP(self,N,flag_ID=0,flag_mode=0):
        g_m = -1 + (1+1)*self.rng.rand() 
        # common value in public
        
        if flag_mode == 0 :
           # fix everything 
            pub_mu = self.comm_mu
            r =  0.8 
        elif flag_mode == 1:
             # fix pub_mu and randomize r 
            pub_mu = self.comm_mu                
            r =  0.8 + 0.15*self.rng.rand() 
        elif flag_mode == 2: 
            # fix the r and randomize pub_mu
            pub_mu = self.comm_mu + g_m
            r =  0.8 
        else:
            # randomize everything
            pub_mu = self.comm_mu + g_m
            r =  0.8 + 0.1*self.rng.rand()
        
        SIGMA2 = self.info_para.SIGMA2
        
        x_signal=np.ones(N)
        EVX=self.info_para.vi_mu+(self.info_para.comm_var/self.info_para.xi_sigma2)*(min(x_signal)-self.info_para.xi_mu)
        while EVX < r*pub_mu:
        
            x_signal=self.rng.multivariate_normal(np.ones(N) *(pub_mu*r*1.1),SIGMA2)
            EVX=self.info_para.vi_mu+(self.info_para.comm_var/self.info_para.xi_sigma2)*(min(x_signal)-self.info_para.xi_mu)
            
#        self.info_para.MU=np.ones([N,1])*pub_mu*r*1.1
#        self.info_para.vi_mu=pub_mu*r*1.1
#        
        if flag_ID==1:
            
            info_index=1
        else:
            info_index=0

        
        ladder=0.015 + 0.02*self.rng.rand()
        
        return [pub_mu,x_signal,r,info_index,ladder]
    
    
    
    def signal_DGP_mul(self,N,SS,flag_ID=0,flag_mode=0):
        g_m = -1 + (1+1)*self.rng.rand(SS)
        
        if flag_mode == 0 :
           # fix everything 
            pub_mu = self.comm_mu*np.ones(SS)
            r =  0.8 *np.ones(SS)
        elif flag_mode == 1:
             # fix pub_mu and randomize r 
            pub_mu = self.comm_mu*np.ones(SS)                
            r =  0.8 + 0.15*self.rng.rand(SS) 
        elif flag_mode == 2: 
            # fix the r and randomize pub_mu
            pub_mu = self.comm_mu*np.ones(SS) + g_m
            r =  0.8 *np.ones(SS)
        else:
            # randomize everything
            pub_mu = self.comm_mu*np.ones(SS) + g_m
            r =  0.8 + 0.1*self.rng.rand(SS)
            
    
        SIGMA2 = self.info_para.SIGMA2        
        x_signal=self.rng.multivariate_normal(np.array(N) *(pub_mu*r),SIGMA2,SS*2)
        x_signal_min=x_signal.min(axis=1)
        x_signal=x_signal[x_signal_min>r[0]*pub_mu[0]]
        
        if x_signal.size < SS:
            x_signal=self.rng.multivariate_normal(np.ones(N) *(pub_mu*r),SIGMA2,SS*3)
        
            x_signal=x_signal[x_signal>(r*pub_mu)]
        
        
        x_signal=x_signal[:SS]
        
        if flag_ID==1:
            
            info_index=np.ones(SS)
        else:
            info_index=np.zeros(SS)
            
        ladder=0.02 + 0.02*self.rng.rand()
        return [pub_mu,x_signal,r,info_index,ladder]
    
    
    def interp_update_rule(self,N,E_update_rule,T_p_old,T_p_new,xi_v_old,xi_v_new):
        # given the large bidding function result, I interp current simulation 
        # bidding function
        # possibly abbandon in the future
        
        interp_mesh = np.array(np.meshgrid(xi_v_new, T_p_new,T_p_new,T_p_new))
        interp_points = np.rollaxis(interp_mesh, 0, 5).reshape((interp_mesh/(1+N), 1+N))
        
        
        return interpn((xi_v_old,T_p_old,T_p_old,T_p_old), E_update_rule, interp_points)
    
    
    def Data_simu(self,N,SS,T_end,info_flag=0,flag_mode=0):
        # functions for simulating the bidding path given the numebr of simualted times
        
        # initilize the updating rule 
        Env             =ENV(N, self.dict_para)
        self.info_para  =Env.Uninform()
            
        Update_bid=Update_rule(self.info_para)
        
        data_act=np.ones((SS,T_end),dtype=int)*(-1)  # bidding path 
        pub_info=np.zeros((SS,5))
        data_state=np.zeros((SS,N),dtype=int)  # current posting bid position for each bidder
        data_bid_freq=np.zeros((SS,N)) # each bidders bidding times 
        data_win=np.zeros((SS,1))

        freq_i1 = np.zeros((SS,1))
        freq_i2 = np.zeros((SS,1))
        
        num_i = np.zeros((SS,1),dtype=int)
        sec_diff_i1=np.zeros((SS,1))
        sec_diff_i2=np.zeros((SS,1))
        sec_freq_i1=np.zeros((SS,1))
        sec_freq_i2=np.zeros((SS,1))
        low_freq_ratio_i=np.zeros((SS,1))
        
        third_win_i=np.zeros((SS,1))

        # [pub_mu_v,x_signal_v, reserve_v,info_index,ladder]=self.signal_DGP_mul(N,int(SS),info_flag,flag_mode)
        # Active_flag=np.ones(N)
        for s in range(0,SS):
            # x_signal=x_signal_v[s,:]
            # pub_mu=pub_mu_v[s]
            # reserve=reserve_v[s]
            
            [pub_mu,x_signal, reserve,info_index,ladder]=self.signal_DGP(N,info_flag,flag_mode)
            pub_info[s,:]=[pub_mu, reserve,N,info_index,ladder]
            

            price_v = np.array(range(1,T_end+1))*ladder + pub_mu*reserve
            price_v = np.append(pub_mu*reserve,price_v)

            self.T_p=price_v
            
            State = np.zeros(N,dtype=int)
            Active= np.ones(N,dtype=int)
            
            
            for t in range(0,T_end):
                
                if t == 0: 
                    curr_bidder=int(np.argmax(x_signal))
                    data_act[s,t] = curr_bidder
                    State[curr_bidder]=State[curr_bidder]+1
                else:
                    
                    for i in range(0,N):
                        temp_state=copy.deepcopy(State)
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)

                        ss_state = [ii]
                        ss_state = ss_state + temp_state.tolist()
               
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
                            State[curr_bidder] = bid
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
                        State[curr_bidder] = bid
           
        
            # final state
            # notice there exist mismatch between data act and state 
            # state is right data act need to add 1 
            try:
                data_state[s,:]=State
                
                # calculate the bidding frequency for each bidders 
                unique, counts = np.unique(data_act[s,:], return_counts=True)
    
    #            freq_list=[x for x in zip(unique,counts) if x[0] != -1]
    #            data_bid_freq[s,:]=np.array(freq_list)
                
                a=zip(unique,counts) 
                for ele in a:
                    if ele[0] != -1:
                        data_bid_freq[s,int(ele[0])]=ele[1]
                
                
                
                # calculate the real bidding number 
                temp_freq=[x for x in data_bid_freq[s,:] if x > 0]
                freq_i2[s]=np.std(temp_freq)
                freq_i1[s]=np.mean(temp_freq)
                
                
                # winning
                data_win[s]=price_v[int(max(State))] / (pub_mu*reserve)
                
                
                
                ## new adding 
                order_ind=np.argsort(State)
                # second higest bidder to the difference
                
                i_ed = order_ind[-2]
                i_rest =order_ind[:-2]
                temp_pos=(State[i_ed] - np.array(State[i_rest]))
                
                sec_diff_i1[s]= np.mean(temp_pos)
                sec_diff_i2[s]= np.std(temp_pos)
                
                # lower rank freq 
                low_freq_list=[]
                
                freq_list=[x for x in zip(unique,counts) if x[0] != -1]
                freq_sum=[x[1] for x in zip(unique,counts) if x[0] != -1]
                for ele in freq_list:
                    if ele[0] != order_ind[-1] and ele[0] != order_ind[-2]:
                        low_freq_list.append(ele[1])
                
                if len(low_freq_list)==0 :
                    sec_freq_i1[s]=0
                    sec_freq_i2[s]=np.nan
                    low_freq_ratio_i[s]=0
                else:
                    sec_freq_i1[s]=np.nanmean(low_freq_list)
                    sec_freq_i2[s]=np.nanstd(low_freq_list)
                    low_freq_ratio_i[s]=sum(low_freq_list)/sum(freq_sum)
                
                
                # find real bidding bidders
                num_i[s]  =int(sum((State>0)*1))
                pub_info[s,2]=num_i[s]
                
                
                
                # third highest winning price (relative)
                if N>=3:
                    third_win_i[s] = price_v[State[order_ind[-3]]]/ (pub_mu*reserve)
                else:
                    third_win_i[s] = np.nan
            except Exception as e:
                print(e)
                print('s:{},State:{},act:{}'.format(s,State,data_act[s,]))

        
        data_dict={
                'data_act':data_act,
                'pub_info':pub_info,
                'data_state':data_state,
                'data_bid_freq':data_bid_freq,
                'data_win':data_win,
                'num_i':num_i,

                'freq_i1':freq_i1,
                'freq_i2':freq_i2,
                
                'sec_diff_i1':sec_diff_i1,
                'sec_diff_i2':sec_diff_i2,
                'sec_freq_i1':sec_freq_i1,
                'sec_freq_i2':sec_freq_i2,
                'low_freq_ratio_i' :low_freq_ratio_i,
                'third_win_i':third_win_i,
                
                }
        

        return data_struct(data_dict)

    def Data_simu_info(self,N,SS,T_end,info_flag=1,flag_mode=0):
        # functions for simulating the bidding path given the numebr of simualted times
        
        # initilize the updating rule 
        Env       =ENV(N, self.dict_para)
        self.info_para  =Env.Info_ID()
        
        Update_bid=Update_rule(self.info_para)
        
        data_act=np.ones((SS,T_end),dtype=int)*(-1)  # bidding path 
        pub_info=np.zeros((SS,5))
        data_state=np.zeros((SS,N),dtype=int)  # current posting bid position for each bidder
        data_bid_freq=np.zeros((SS,N)) # each bidders bidding times 
        data_win=np.zeros((SS,1))

        freq_i1 = np.zeros((SS,1))
        freq_i2 = np.zeros((SS,1))
        
        num_i = np.zeros((SS,1),dtype=int)

        sec_diff_i1=np.zeros((SS,1))
        sec_diff_i2=np.zeros((SS,1))
        sec_freq_i1=np.zeros((SS,1))
        sec_freq_i2=np.zeros((SS,1))
        low_freq_ratio_i=np.zeros((SS,1))
        
        third_win_i=np.zeros((SS,1))

        # [pub_mu_v,x_signal_v, reserve_v,info_index]=self.signal_DGP_mul(int(SS),info_flag,flag_mode)
        # Active_flag=np.ones(N)
        for s in range(0,SS):
            # x_signal=x_signal_v[s,:]
            # pub_mu=pub_mu_v[s]
            # reserve=reserve_v[s]
            
            [pub_mu,x_signal, reserve,info_index,ladder]=self.signal_DGP(N,info_flag,flag_mode)
            pub_info[s,:]=[pub_mu, reserve,N,info_index,ladder]
            

            price_v = np.array(range(1,T_end+1))*ladder + pub_mu*reserve
            price_v = np.append(pub_mu*reserve,price_v)
            # pub_info[s,:]=[pub_mu, reserve,N,info_index[s]]
            # n_Tend=int((T_end-10)/2)
            # price_v = np.linspace(reserve*pub_mu,pub_mu*1.1, n_Tend)
            # price_v=np.append(price_v,np.linspace(1.12*pub_mu,pub_mu*1.8, n_Tend))
            # price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,int(T_end-2*n_Tend)))
            
            self.T_p=price_v
            
            State = np.zeros(N,dtype=int)
            Active= np.ones(N,dtype=int)
            
            
            for t in range(0,T_end):
                
                if t == 0: 
                    curr_bidder=int(np.argmax(x_signal))
                    data_act[s,t] = curr_bidder
                    State[curr_bidder]=State[curr_bidder]+1
                else:
                    
                    
                    
                    for i in range(0,N):
                        temp_state=copy.deepcopy(State)
                        if i !=1:
                            
                            
                            ii = int(temp_state[i])
                            i_info=int(temp_state[1])
                            temp_state=np.delete(temp_state,[i,1])
    
                            ss_state = [ii,i_info]
                            ss_state = ss_state + temp_state.tolist()
                   
                            bid = max(ss_state)+1
                            result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
                            
                            
                        else:
                            bid = max(temp_state)+1
                            Evx=x_signal[i]
                            result=[Evx,Evx-price_v[bid],1*(Evx-price_v[bid]>0)]
                            
                        Active[i] = result[2]
                            
                        
                    if sum(Active) ==1:
                        index=np.nonzero(Active)[0].tolist()
                        
                        posting=data_act[s,t-1]
                        if index == posting:
                            data_act[s,t:] = int(-1)
                        else:
                            curr_bidder      = int(index[0])
                            data_act[s,t]    = int(curr_bidder)
                            State[curr_bidder] = bid
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
                        State[curr_bidder] = bid
           
        
            # final state
            # notice there exist mismatch between data act and state 
            # state is right data act need to add 1 
            try:
                data_state[s,:]=State
                
                # calculate the bidding frequency for each bidders 
                unique, counts = np.unique(data_act[s,:], return_counts=True)
    
    #            freq_list=[x for x in zip(unique,counts) if x[0] != -1]
    #            data_bid_freq[s,:]=np.array(freq_list)
                
                a=zip(unique,counts) 
                for ele in a:
                    if ele[0] != -1:
                        data_bid_freq[s,int(ele[0])]=ele[1]
                    else:
                        continue
                
                
                # calculate the real bidding number 
                temp_freq=[x for x in data_bid_freq[s,:] if x > 0]
                freq_i2[s]=np.std(temp_freq)
                freq_i1[s]=np.mean(temp_freq)
                
                
                # winning
                data_win[s]=price_v[int(max(State))] / (pub_mu*reserve)
                
                
                
                ## new adding 
                order_ind=np.argsort(State)
                # second higest bidder to the difference
                
                i_ed = order_ind[-2]
                i_rest =order_ind[:-2]
                temp_pos=(State[i_ed] - np.array(State[i_rest]))
                
                sec_diff_i1[s]= np.mean(temp_pos)
                sec_diff_i2[s]= np.std(temp_pos)
                
                # lower rank freq 
                low_freq_list=[]
                
                freq_list=[x for x in zip(unique,counts) if x[0] != -1]
                freq_sum=[x[1] for x in zip(unique,counts) if x[0] != -1]
                for ele in freq_list:
                    if ele[0] != order_ind[-1] and ele[0] != order_ind[-2]:
                        low_freq_list.append(ele[1])
                
                if len(low_freq_list)==0 :
                    sec_freq_i1[s]=0
                    sec_freq_i2[s]=np.nan
                    low_freq_ratio_i[s]=0
                else:
                    sec_freq_i1[s]=np.nanmean(low_freq_list)
                    sec_freq_i2[s]=np.nanstd(low_freq_list)
                    low_freq_ratio_i[s]=sum(low_freq_list)/sum(freq_sum)
                
                
                # find real bidding bidders
                num_i[s]  =int(sum((State>0)*1))
                pub_info[s,2]=num_i[s]
                
                
                
                # third highest winning price (relative)
                if N>=3:
                    third_win_i[s] = price_v[State[order_ind[-3]]]/ (pub_mu*reserve)
                else:
                    third_win_i[s] = np.nan
            except Exception as e:
                print(e)
                print('s:{},State:{},act:{}'.format(s,State,data_act[s,]))

        
        data_dict={
                'data_act':data_act,
                'pub_info':pub_info,
                'data_state':data_state,
                'data_bid_freq':data_bid_freq,
                'data_win':data_win,
                'num_i':num_i,

                'freq_i1':freq_i1,
                'freq_i2':freq_i2,
                
                'sec_diff_i1':sec_diff_i1,
                'sec_diff_i2':sec_diff_i2,
                'sec_freq_i1':sec_freq_i1,
                'sec_freq_i2':sec_freq_i2,
                'low_freq_ratio_i' :low_freq_ratio_i,
                'third_win_i':third_win_i,
                
                }
        
        
        

        return data_struct(data_dict)
            
class data_struct:
    def __init__(self,data_dict):
        self.data_dict=data_dict
        
    @property 
    def data_act(self):
        '''
        return data_act
        '''
        return self.data_dict['data_act']

    @property 
    def pub_info(self):
        '''
        return pub_info
        '''
        return self.data_dict['pub_info']

    @property 
    def data_state(self):
        '''
        return data_state
        '''
        return self.data_dict['data_state']

    @property 
    def data_bid_freq(self):
        '''
        return data_bid_freq
        '''
        return self.data_dict['data_bid_freq']

    @property 
    def data_win(self):
        '''
        return data_win
        '''
        return self.data_dict['data_win']
    
    @property 
    def data_win2(self):
        '''
        return data_win2
        '''
        return np.square(self.data_dict['data_win']-np.mean(self.data_dict['data_win']))

    @property 
    def num_i(self):
        '''
        return num_i
        '''
        return self.data_dict['num_i']
    
    
    @property 
    def num_i2(self):
        '''
        return num_i2 
        '''
        return np.square(self.data_dict['num_i']-np.mean(self.data_dict['num_i']))
        
    
    @property
    def freq_i1(self):
        '''
        return freq_distance_i
        '''
        return self.data_dict['freq_i1']
    
    @property
    def freq_i2(self):
        '''
        return freq_distance_i2
        '''
        return self.data_dict['freq_i2']
    
    
    
    @property
    def sec_diff_i1(self):
        '''
        return sec_diff_i1
        '''
        return self.data_dict['sec_diff_i1']
    
    @property
    def sec_diff_i2(self):
        '''
        return freq_distance_i2
        '''
        return self.data_dict['sec_diff_i2']
    
    @property
    def sec_freq_i1(self):
        '''
        return sec_freq_i1
        '''
        return self.data_dict['sec_freq_i1']
    
    @property
    def sec_freq_i2(self):
        '''
        return sec_freq_i2
        '''
        return self.data_dict['sec_freq_i2']

    @property
    def low_freq_ratio_i(self):
        '''
        return tot_freq_i
        '''
        return self.data_dict['low_freq_ratio_i']
    
    @property
    def third_win_i(self):
        '''
        return third_win_i
        '''
        return self.data_dict['third_win_i']
    
