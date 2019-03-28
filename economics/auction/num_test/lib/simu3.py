# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 19:07:30 2019

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

--03-19-2019--
1 add the threshold for the informed bidder
2 reorganize the problem and algorithm

--03-26-2019--
1 add truncated normal generator for random vector
"""

import numpy as np
import pandas as pd
from Update_rule_simu2 import Update_rule
from GHK import GHK
from scipy.interpolate import interpn
from scipy.stats import norm,truncnorm
from ENV import ENV 
import scipy.linalg as LAA
import copy,random
import scipy.stats as ss

import warnings
# warnings.filterwarnings('error')

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
              'real_num_bidder','win_norm', 'num_bidder','winning_ID','res_norm','signal_max_ID']
Col_name_pre=['ID','info_bidder_ID','winning_ID','dict_para','x_v','post_price','ladder_norm','signal_max_ID','real_num','win_norm','win2_norm']

class Simu:
    def __init__(self,rng_seed=123,dict_para=para_dict,bidding_mode=0,eq_premium=0):
        '''
        rng_seed: controls the random seed 
        dict_para: the parameter set
        bidding mode: control for the informed bidder's bidding strategy
                      0-> normal case 
                      1-> every time when she can bid, she will win that position
                      2-> never bid   

        '''

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
        self.bidding_mode = bidding_mode 
        self.eq_premium = eq_premium

    def rand_reserve(self,mode):
        '''
        mode controls for random or not 
        '''
        if mode == 0:
            reserve = 1.0
        else:
            reserve = 0.7 + 0.3*self.rng.rand() 
        return reserve

    def randomize_para(self):
        dict_para={}
        dict_para['comm_mu']     = (-0.15  + 0.3*self.rng.rand())
        dict_para['beta']        = 0
        dict_para['comm_var']    = (0.2*self.rng.rand())
        dict_para['priv_var']    = (0.2*self.rng.rand())
        dict_para['epsilon_var'] = (0.2*self.rng.rand())
        return dict_para
        
    def signal_DGP_simu(self,para,rng,N,X_bar,X_up,JJ=10):
        # generate the random vectors for simulation 
        # is_sorted = lambda a: np.all(a[:-1] <= a[1:])
        MU       =para.MU[0] 
        MU       =MU.flatten()
        SIGMA2   =para.SIGMA2[0]   

        flag=True
        while flag:
            # check 
            x_signal     = self.rng.multivariate_normal(MU,SIGMA2,int(JJ*N))
            # x_signal = truncnorm.rvs(MU,SIGMA2,X_bar,size=int(JJ*N),random_state=rng)
            # x_signal = x_signal.reshape(JJ,N)

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
        ladder=0.01 + 0.015*self.rng.rand()
        
        return [x_signal[0,],ladder]


    def para_ghk(self,para,i_id):
        '''
        Set up the parameters for the each bidder
        '''
        para_dict={}
        para_dict['MU']           = para.MU[i_id]
        para_dict['SIGMA2']       = para.SIGMA2[i_id]
        para_dict['N']            = para.N
        # dimension
        #             
        para_dict['MU']              = para_dict['MU'].reshape(para.N,1)
        return para_dict


    def Data_simu(self,N,SS,info_flag=0,T_end=70):
        '''
        functions for simulating the bidding path given the numebr of simualted times
        entry threshold is important 

        several simulation mode: 
        1. random_para_flag : indicate whether it fixes the parameter set (0) or randomize (1) 
        2. reserve_flag     : indicate whether it fixes the reserve price (0) or not (1)
        3. rule_flag        : indicates what kinds of upper bound constraint we use (0- no upper bound) (1 upper bounds) (2 xi and upper bound)
        '''
        reserve_flag = 0
        random_para_flag = 0
        rule_flag  = 1
        # prepared vector
        Sim_df=pd.DataFrame(columns=Col_name)


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
        ID_i=np.zeros((SS,1)) # winner id 
        third_win_i=np.zeros((SS,1)) # third winner winning id
        second_win_i=np.zeros((SS,1))

        # start the simulation
        for s in range(0,SS):
            # select simualtion mode 
            # 1 randomize the reserve price of not 

            # fix the reserve price 
            reserve=self.rand_reserve(reserve_flag)
            Env=ENV(N,self.dict_para)

            # this may be use for differentilize the 
            # constant for each oder of bidding
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
            para=Env.info_struct(info_index_v,rank_index,reserve)

            # initialize updating rule
            Update_bid=Update_rule(para,rule_flag)
            # get the threshold
            Update_bid.setup_para(i_id)
            # entry threehold
            if info_flag==1:
                x_reserve = Update_bid.entry_threshold_info(np.log(reserve))
                # both use the highest entry threshold 
                X_low = x_reserve[0]*np.ones(N)
                X_low[info_index]=x_reserve[1]
            else:
                x_reserve = Update_bid.threshold_test(np.log(reserve))
                X_low=x_reserve*np.ones([1,N])

            # select highest x_bar as entry conditions 
            
            # X_up  = Update_bid.entry_simu_up(X_low.flatten(),3)
            X_up = 5
            # ghk_para=self.para_ghk(para,0)
            # ghk=GHK(ghk_para)
            # [x_signal,w_v] = ghk.GHK_simulator(X_low,X_up*np.ones(N),2,4488,100)
            # x_signal=x_signal[:,-1].flatten()
            # ladder=0.01 + 0.015*self.rng.rand()

            [x_signal,ladder]=self.signal_DGP_simu(para,self.rng,N,X_low,X_up*np.ones([1,N]))
            
            # notice that actually, I do not need to vectorize the bidding price
            # I can just use the bidding ladder and reserve price to represent posting 
            # price at each period 
            # this can be done for the state variable
            
            State = np.ones(N,dtype=int)*(-1)
            Active= np.zeros(N,dtype=int)
            Active2=np.zeros(N)
            Data_act=[]
            auction_flag=True
            t=0 # auction period
            # up to now, I exclude the jump bid 
            while auction_flag and t <= 300:
                
                if t == 0: 
                    curr_bidder=self.rng.choice(range(N),size=1)[0] 
                    # bidding mode 2 -> informed bidder is the active bidder 
                    if self.bidding_mode ==2 and info_flag==1:
                        curr_bidder=info_index
                    
                    Data_act.append(curr_bidder)
                    State[curr_bidder]=State[curr_bidder]+1
                else:

                    for i in range(0,N):
                        temp_state=copy.deepcopy(State)
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)

                        ss_state = np.append(ii,temp_state)
                        # convert state to the history price 
                        ss_state_p = np.array([reserve + max(t_ele,0)*ladder for t_ele in ss_state ]) 

                        bid = max(ss_state)+1
                        # next posting price 
                        Update_bid.setup_para(i)
                        bid_price = reserve + bid * ladder
                        no_flag =  1*(np.array(ss_state)>-1)[1:] 
                        
                        result = Update_bid.real_bid(x_signal[i],ss_state_p,bid_price,no_flag,i) if i != info_index else Update_bid.real_info_bid(x_signal[i],bid_price)
                        
                        Active[i]  = result[2]
                        Active2[i] = result[1]
                        
                    if sum(Active) == 0:
                        # all quit
                        auction_flag=False
                        break

                    elif sum(Active) ==1:
                        # only one remains
                        current_bidder=int(np.nonzero(Active)[0].tolist()[0])
                        
                        if current_bidder != Data_act[t-1]:
                            Data_act.append(current_bidder)
                            State[current_bidder] = bid
                        auction_flag=False
                        break

                    else :
                        # normal biddig
                        posting=Data_act[t-1]
                        index=np.nonzero(Active)[0].tolist()
                        if posting in index :
                            index.remove(posting)
                        
                        curr_bidder   = self.rng.choice(index,size=1) 

                        if self.bidding_mode ==1: 
                            if info_index in index:
                                curr_bidder=info_index
                        elif self.bidding_mode ==2 and info_index in index:
                            index.remove(info_index)
                            if len(index)>0:
                                curr_bidder   = self.rng.choice(index,size=1)
                            else:
                                auction_flag=False
                                break


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
                data_win[s]    = reserve + max(State)*ladder 
                
                # second higest bidder to the difference
                order_ind=np.argsort(State)
                i_ed = order_ind[-2]
                i_rest =order_ind[:-2]
                if N>3:
                    temp_pos=(State[i_ed] - np.array(State[i_rest]))
                    # third highest winning price (relative)
                    third_win_i[s] = reserve + State[order_ind[-3]]*ladder  
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
                signal_max=np.argsort(x_signal)[-1]

            except Exception as e:
                print(e)
                print('s:{},State:{},act:{}'.format(s,State,Data_act))
            # Col_name=['ID', 'bidder_act', 'len_act','info_bidder_ID', 'bidder_state','bidder_price','ladder_norm',
            #   'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm','x_signal_max']
            State_PP = [reserve + s_ele*ladder for s_ele in State] 
            temp_series=pd.Series([s,Data_act,len(Data_act),info_index,State,State_PP,ladder,int(sum((State>0)*1)),reserve + max(State)*ladder,N,order_ind[-1],reserve,signal_max ], index=Col_name )
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

    def setup_para(self,data_df):
        self.dict_df=data_df['dict_para'].tolist()
        self.x_v    =data_df['x_v'].tolist()
        self.l_ladder = data_df['ladder_norm'].tolist()


    def Data_premium(self,N,SS,info_flag=1,mode_flag=0):
        premium_df=pd.DataFrame(columns=Col_name_pre)

        for s in range(0,SS):
            # select simualtion mode 
            # 1-> random parameter set
            # 2-> fix the parameter set
            # 3-> fix the reserve price 

            # random parameter set in each time 
            # dict_para = self.randomize_para()
            # Env=ENV(N, dict_para)

            # fix the parameter set
            self.reserve=1
            if info_flag==1:
                dict_para=self.randomize_para()
            else:
                dict_para=self.dict_df[s]
                x_signal =self.x_v[s]
                ladder   =self.l_ladder[s]
            Env=ENV(N,dict_para)
            # ordered index for the bidders remove
            rank_index=np.ones(N)
            # informed or not informed
            info_index_v= np.ones(N)
            i_id = 0 
            if info_flag==1:            
                info_index  = int(np.random.randint(0,N,size=1))
                info_index_v[info_index]=0
                
                # argument for info_struct info_index,ord_index,res
                para=Env.info_struct(info_index_v,rank_index,1)

                X_bar = (-10)*np.ones([1,N])
                X_up  = (10)*np.ones([1,N])
                
                [x_signal,ladder]=self.signal_DGP_simu(para,self.rng,N,X_bar,X_up)
                # reorder the x_singal! 
                # rank order of x_signal

                ri_ind       = ss.rankdata(x_signal)
                ri_ind       = ri_ind-1
                info_index_v = np.ones(N)
                info_index   = (N-1)-ri_ind[int(info_index)]
                info_index_v[int(info_index)]=0
            else:
                info_index = -1
            Env  =ENV(N,dict_para)
            para =Env.info_struct(info_index_v,rank_index,1)
            x_signal=np.sort(x_signal)[::-1]

            # initialize updating rule
            Update_bid=Update_rule(para)
            Update_bid.setup_para(0)
            price_vector=Update_bid.get_HS_drop_p(x_signal)
            # add the T1 criterion that any bid not satifying the bidding sequence should be abandoned 
            # but it would be difficult to apply 

            win_bid       = max(price_vector)
            win_bid_2     = np.sort(price_vector)[-2]
            win_bid_id    = np.argsort(price_vector)[-1]
            x_signal_id   = np.argsort(x_signal)[-1]
            # Col_name_pre=['ID','info_bidder_ID','winning_ID','dict_para','x_v','post_price','ladder_norm','signal_max_ID','real_num','win_norm','win2_norm']

            temp_series   = pd.Series([s,info_index,win_bid_id,dict_para,x_signal,price_vector,ladder,x_signal_id,N,win_bid,win_bid_2], index=Col_name_pre )
            premium_df=premium_df.append(temp_series, ignore_index=True)
            
        return premium_df


