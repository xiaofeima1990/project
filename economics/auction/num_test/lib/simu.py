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
 
delete the rank order assumption
Q1 why I can not generate corresponding N active bidders? 
because the auctioneer random pick the candidate at each period. Someone may have lower signal which will drop very early.
Another way is to change the picking rule. let lower valued guy bidding first 

it is somehow much complicated than I can image
But I want to use this to generate :
informed bidder's bidding status 
the distribution of number of bidders

"""

import numpy as np
import pandas as pd
from Update_rule_simu import Update_rule
from scipy.interpolate import interpn
from ENV import ENV 
import scipy.linalg as LAA
import copy
import random
import scipy.stats as ss
import warnings
warnings.filterwarnings('error')

para_dict={
        "comm_mu":0.2,
        "priv_mu":0,  # fix
        "beta":0.1,
        "epsilon_mu":0,
        "comm_var":0.3,
        "priv_var":0.15,
        "epsilon_var":0.2,
        }


Col_name=['ID', 'bidder_act', 'len_act','info_bidder_ID', 'bidder_state','bidder_price','ladder_norm',
              'real_num_bidder','win_norm', 'num_bidder','winning_ID','res_norm']

class Simu:
    def __init__(self,rng_seed=123,dict_para=para_dict):


        self.rng       =np.random.RandomState(rng_seed)
                
        self.comm_mu   =dict_para['comm_mu']
        self.priv_mu   =0
        # self.epsilon_mu   = dict_para['epsilon_mu']
        self.epsilon_mu   = 0
        self.beta = dict_para['beta']
        self.comm_var  =dict_para['comm_var']
        self.priv_var  =dict_para['priv_var']
        self.noise_var =dict_para['epsilon_var']
        self.dict_para =dict_para

    def rand_reserve(self,mode):
        '''
        mode controls for random or not 
        '''
        if mode == 0:
            self.reserve = 0.8
        else:
            self.reserve =   0.7 + 0.3*self.rng.rand() 
        

    def randomize_para(self):
        dict_para={}
        dict_para['comm_mu']     = self.dict_para['comm_mu']+ (-0.075  + 0.15*self.rng.rand())
        dict_para['comm_var']    = self.dict_para['comm_var']+ (-0.05 + 0.1*self.rng.rand())
        dict_para['priv_var']    = self.dict_para['priv_var']+ (-0.05 + 0.1*self.rng.rand())
        dict_para['epsilon_var'] = self.dict_para['epsilon_var']+ (-0.05 +  0.1*self.rng.rand())
        dict_para['beta']        = self.dict_para['beta']
        return dict_para
        
    def signal_DGP_simu(self, para,rng,N,X_bar,X_up, JJ=10):
        # generate the random vectors for simulation 
        # is_sorted = lambda a: np.all(a[:-1] <= a[1:])
        MU       =para.MU[0] 
        MU       =MU.flatten()
        SIGMA2   =para.SIGMA2[0]   

        flag=True
        while flag:
            # check 
            x_signal=self.rng.multivariate_normal(MU,SIGMA2,int(JJ*N))

            # entry selection 
            check_flag   = x_signal  > X_bar.reshape(1,X_bar.size)
            check_flag_v = np.prod(check_flag, axis=1)
            check_flag2  = x_signal < X_up.reshape(1,X_up.size)
            check_flag_v2=np.prod(check_flag2, axis=1)
            check_flag_v = check_flag_v * check_flag_v2
            check_flag_v=check_flag_v.astype(bool)

            if len(x_signal[check_flag_v,]) >0:
                x_signal=x_signal[check_flag_v,]
                flag=False
        
        # bidding ladder
        ladder=0.015 + 0.015*self.rng.rand()
        
        return [x_signal[0,],ladder]


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


    def Data_simu(self,N,SS,info_flag=0,T_end=70):
        # functions for simulating the bidding path given the numebr of simualted times
        

        # prepared vector
        Sim_df=pd.DataFrame(columns=Col_name)

        # data_act_v=np.ones((SS,T_end),dtype=int)*(-1)  # bidding path 
        
        data_bid_freq= [] # each bidders bidding times 
        data_win     = np.zeros((SS,1))
        data_win_pos = np.zeros((SS,1))

        freq_i1 = np.zeros((SS,1))
        freq_i2 = np.zeros((SS,1))
        
        num_i = np.zeros((SS,1),dtype=int)
        sec_diff_i1=np.zeros((SS,1))
        sec_diff_i2=np.zeros((SS,1))
        sec_freq_i1=np.zeros((SS,1))
        sec_freq_i2=np.zeros((SS,1))
        low_freq_ratio_i=np.zeros((SS,1))
        ID_i=np.zeros((SS,1))
        third_win_i=np.zeros((SS,1))

        # start the simulation
        for s in range(0,SS):
            # select simualtion mode 
            # 1-> random parameter set
            # 2-> fix the parameter set
            # 3-> fix the reserve price 

            # random parameter set in each time 
            # dict_para = self.randomize_para()
            # Env=ENV(N, dict_para)

            # fix the parameter set
            self.rand_reserve(0)
            Env=ENV(N,self.dict_para)

            # ordered index for the bidders remove
            rank_index=np.ones(N)
            # informed or not informed
            info_index_v= np.ones(N)
            i_id = 0 
            if info_flag==1:            
                info_index  = int(np.random.randint(0,N,size=1))
                info_index_v[info_index]=0
                
            else:
                info_index = -1

            # argument for info_struct info_index,ord_index,res
            para=Env.info_struct(info_index_v,rank_index,self.reserve)

            # initialize updating rule
            Update_bid=Update_rule(para)

            Update_bid.setup_para(i_id)
            X_bar = Update_bid.entry_threshold(self.reserve*np.ones([N,1]))
            # select highest x_bar as entry conditions 
            X_bar = max(X_bar)*np.ones([1,N])
            X_up  = Update_bid.entry_simu_up(X_bar.flatten(),2.5)
            
            [x_signal,ladder]=self.signal_DGP_simu(para,self.rng,N,X_bar,X_up*np.ones([1,N]))
            pub_info=[self.reserve,N,info_index,ladder]
            
            # notice that actually, I do not need to vectorize the bidding price
            # I can just use the bidding ladder and reserve price to represent posting 
            # price at each period 
            # this can be done for the state variable
            
            State = np.ones(N,dtype=int)*(-1)
            Active= np.zeros(N,dtype=int)
            Data_act=[]
            auction_flag=True
            t=0 # auction period
            # up to now, I exclude the jump bid 
            while auction_flag and t <= 300:
                
                if t == 0: 
                    curr_bidder=self.rng.choice(range(N),size=1)[0] 
                    
                    Data_act.append(curr_bidder)
                    State[curr_bidder]=State[curr_bidder]+1
                else:

                    for i in range(0,N):
                        temp_state=copy.deepcopy(State)
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)

                        ss_state = [ii]
                        ss_state = ss_state + temp_state.tolist()
                        # convert state to the history price 
                        ss_state_p = np.array([self.reserve + max(t_ele,0)*ladder for t_ele in ss_state ]) 

                        bid = max(ss_state)+1
                        # next posting price 
                        # change
                        Update_bid.setup_para(i)
                        bid_price = self.reserve + bid * ladder
                        no_flag =  1*(np.array(ss_state)>-1)[1:] 
                        if i != info_index:
                            result = Update_bid.real_bid(x_signal[i],ss_state_p,bid_price,no_flag,i)
                        else:
                            result = Update_bid.real_info_bid(x_signal[i],bid_price)
                        
                        Active[i] = result[2]
                        
                    if sum(Active) == 0:
                        auction_flag=False
                        break

                    elif sum(Active) ==1:
                        index=np.nonzero(Active)[0].tolist()[0]
                        
                        posting=Data_act[t-1]
                        if index != posting:
                            curr_bidder        = int(index)
                            Data_act.append(int(curr_bidder)) 
                            State[curr_bidder] = bid
                        auction_flag=False
                        break

                    else :
                        posting=Data_act[t-1]
                        index=np.nonzero(Active)[0].tolist()
                        if posting in index :
                            index.remove(posting)

                        curr_bidder   = self.rng.choice(index,size=1) 
                        Data_act.append(int(curr_bidder)) 
                        State[curr_bidder] = bid
                # add t
                t += 1
            #--------------------------------------
            # the bidding path construction end
            #--------------------------------------

            #--------------------------------------
            # moments construction
            #--------------------------------------
            # notice there exist mismatch between data act and state 
            # state is right data act need to add 1 
            try:

                # calculate the bidding frequency for each bidders 
                unique, counts = np.unique(Data_act, return_counts=True)
                a=zip(unique,counts)
                temp_bid_freq=np.zeros(N) 
                for ele in a:
                    temp_bid_freq[int(ele[0])]=ele[1]
                
                data_bid_freq.append(temp_bid_freq)

                # calculate the real bidding number 
                temp_freq=[x for x in temp_bid_freq if x > 0]
                freq_i2[s]=np.std(temp_freq)
                freq_i1[s]=np.mean(temp_freq)

                # winning bid
                data_win[s]    = self.reserve + max(State)*ladder 
                
                # second higest bidder to the difference
                order_ind=np.argsort(State)
                i_ed = order_ind[-2]
                i_rest =order_ind[:-2]
                if N>3:
                    temp_pos=(State[i_ed] - np.array(State[i_rest]))
                    # third highest winning price (relative)
                    third_win_i[s] = self.reserve + State[order_ind[-3]]*ladder  
                else:
                    third_win_i[s] = np.nan
                    temp_pos=1
                
                sec_diff_i1[s]= np.mean(temp_pos)
                sec_diff_i2[s]= np.std(temp_pos)
                
                # real number of bidders
                num_i[s]=int(sum((State>0)*1))

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
                
                ID_i[s] = s
                ## find real bidding bidders
                # pub_info[1]=int(sum((State>0)*1))
                
                
                # who wins 
                data_win_pos[s] = order_ind[-1]

            except Exception as e:
                print(e)
                print('s:{},State:{},act:{}'.format(s,State,data_act))
            # Col_name=['ID', 'bidder_act', 'len_act','info_bidder_ID', 'bidder_state','bidder_price','ladder_norm',
            #   'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
            State_PP = [self.reserve + s_ele*ladder for s_ele in State] 
            temp_series=pd.Series([s,Data_act,len(Data_act),info_index,State,State_PP,ladder,int(sum((State>0)*1)),self.reserve + max(State)*ladder,N,order_ind[-1],self.reserve ], index=Col_name )
            Sim_df=Sim_df.append(temp_series, ignore_index=True)

        data_dict={
                'ID':ID_i.flatten(),
                'data_bid_freq':data_bid_freq,
                'data_win':data_win.flatten(),
                'num_i':num_i.flatten(),

                'freq_i1':freq_i1.flatten(),
                'freq_i2':freq_i2.flatten(),
                
                'sec_diff_i1':sec_diff_i1.flatten(),
                'sec_diff_i2':sec_diff_i2.flatten(),
                'sec_freq_i1':sec_freq_i1.flatten(),
                'sec_freq_i2':sec_freq_i2.flatten(),
                'low_freq_ratio_i' :low_freq_ratio_i.flatten(),
                'third_win_i':third_win_i.flatten(),
                }

        Sim_MoM_df=pd.DataFrame.from_dict(data_dict)

        return [Sim_df,Sim_MoM_df]


            
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
    
