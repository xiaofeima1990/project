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


"""

import numpy as np
import pandas as pd
from Update_rule import Update_rule
from scipy.interpolate import interpn
from ENV import ENV 
import scipy.linalg as LAA
import copy
import random
import scipy.stats as ss

para_dict={
        "comm_mu":0.2,
        "priv_mu":0,  # fix
        "epsilon_mu":0.1,
        "comm_var":0.3,
        "priv_var":0.15,
        "epsilon_var":0.2,
        }


Col_name=['ID', 'bidder_act', 'len_act','info_bidder_ID', 'bidder_state','bidder_price','ladder_norm',
              'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']

class Simu:
    def __init__(self,rng_seed=123,dict_para=para_dict):


        self.rng       =np.random.RandomState(rng_seed)
                
        self.comm_mu   =dict_para['comm_mu']
        self.priv_mu   =0
        # self.epsilon_mu   = dict_para['epsilon_mu']
        self.epsilon_mu   = 0
        self.comm_var  =dict_para['comm_var']
        self.priv_var  =dict_para['priv_var']
        self.noise_var =dict_para['epsilon_var']
        self.dict_para =dict_para


    def randomize_para(self):
        dict_para={}
        dict_para['comm_mu']=self.dict_para['comm_mu']+ (-0.075  + 0.15*self.rng.rand())
        dict_para['comm_var']=self.dict_para['comm_var']+ (-0.05 + 0.1*self.rng.rand())
        dict_para['priv_var']=self.dict_para['priv_var']+ (-0.05 + 0.1*self.rng.rand())
        dict_para['epsilon_var']=self.dict_para['epsilon_var']+ (-0.05 +  0.1*self.rng.rand())

        return dict_para
        
    def signal_DGP_simu(self, para,rng,N,X_bar,X_up, JJ=40):

        # is_sorted = lambda a: np.all(a[:-1] <= a[1:])
        MU       =para.MU[-1] 
        MU       =MU.flatten()
        SIGMA2   =para.SIGMA2[-1]


        flag=True
        while flag:
            # check 
            x_signal=self.rng.multivariate_normal(MU,SIGMA2,JJ)

            # entry selection 
            # con_var = para.vi_sigma2 - para.vi_sigma2**2/para.xi_sigma2
            # X_bar = para.xi_sigma2 /para.vi_sigma2 *(np.log(res) - para.vi_mu - 0.5*con_var ) +para.xi_mu
            
            X_bar = X_bar * np.ones([1,N])
            check_flag = x_signal > X_bar
            check_flag_v=np.prod(check_flag, axis=1)
            check_flag2 = x_signal < X_up
            check_flag_v2=np.prod(check_flag2, axis=1)
            check_flag_v = check_flag_v * check_flag_v2
            check_flag_v=check_flag_v.astype(bool)
            if len(x_signal[check_flag_v,]) >0:
                x_signal=x_signal[check_flag_v,]
                flag=False
                # x_check_f=np.apply_along_axis(is_sorted,1,x_signal)
                # if len(x_signal[x_check_f,])>0:
                #     x_signal=x_signal[x_check_f,]
                #     flag=False
                #     break

            

        # # no it is too slowly and memory probelm
        # [x_signal,w_n]=qe.quad.qnwnorm(
        # list(np.full(shape=N,fill_value=JJ,
        #     dtype=np.int)),
        #     list(MU.flatten()),
        #     SIGMA2)
        
        # bidding ladder
        ladder=0.015 + 0.02*self.rng.rand()
        
        return [x_signal[0,],ladder]



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
    
    
    def Data_simu(self,N,SS,info_flag=0,T_end=70):
        # functions for simulating the bidding path given the numebr of simualted times
        
 

        # prepared vector
        Sim_df=pd.DataFrame(columns=Col_name)

        data_act=np.ones((SS,T_end),dtype=int)*(-1)  # bidding path 
        
        data_bid_freq=[] # each bidders bidding times 
        data_win=np.zeros((SS,1))

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

            # generate random ENV in each time 
            dict_para = self.randomize_para()
            Env=ENV(N, dict_para)

            # ordered index for the bidders remove
            # rank_index=np.array(random.sample(range(0, N), N))
            # ord_index =np.argsort(rank_index)
            rank_index=np.ones(N)
            # informed or not informed
            info_index_v= np.ones(N)
            i_id = 0 
            if info_flag==1:            
                info_index  = int(np.random.randint(0,N,size=1))
                info_index_v[info_index]=0
                if info_index ==0 : 
                    i_id = 1
            else:
                info_index = -1




            # argument for info_struct info_index,ord_index,res
            para=Env.info_struct(info_index_v,rank_index)

            # initialize updating rule
            Update_bid=Update_rule(para)

            res =  0.75 + 0.25*self.rng.rand() 
            Update_bid.setup_para(i_id)
            X_bar = Update_bid.entry_selection(res)
            X_up  = Update_bid.entry_simu_up(X_bar,3)
            [x_signal,ladder]=self.signal_DGP_simu(para,self.rng,N,X_bar,X_up)
            pub_info=[res,N,info_index,ladder]
            

            price_v = np.array(range(1,T_end+1))*ladder + res
            price_v = np.append(res,price_v)

            
            State = np.zeros(N,dtype=int)
            Active= np.ones(N,dtype=int)
            Data_act=[]
            auction_flag=True
            t=0 # auction period
            extend_i=0
            while auction_flag and t <= 300:
                
                if t == 0: 
                    curr_bidder=self.rng.choice(range(N),size=1) 
                    
                    Data_act.append(curr_bidder)
                    State[curr_bidder]=State[curr_bidder]+1
                else:


                    for i in range(0,N):
                        temp_state=copy.deepcopy(State)
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)

                        ss_state = [ii]
                        ss_state = ss_state + temp_state.tolist()
               
                        bid = max(ss_state)+1
                        # change
                        Update_bid.setup_para(i)
                        if i != info_index:
                            result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
                        else:
                            result = Update_bid.real_info_bid(x_signal[i],bid,price_v)
                        
                        Active[i] = result[2]
                        
                    if sum(Active) == 0:
                        auction_flag=False
                        break

                    elif sum(Active) ==1:
                        index=np.nonzero(Active)[0].tolist()[0]
                        
                        posting=Data_act[t-1]
                        if index != posting:
                            curr_bidder      = int(index)
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
                # check whether the price path is enough 
                if t>T_end-5+extend_i*T_end:
                    temp_p = np.array(range((extend_i+1)*T_end+1,(extend_i+2)*T_end+1))*ladder + res
                    price_v = np.append(price_v,temp_p)
                    extend_i+=1
            #-----------------------
            # finish the bidding path construction
            #-----------------------

            #-------------------------
            # moments construction
            #-------------------------
            # final state
            # notice there exist mismatch between data act and state 
            # state is right data act need to add 1 
            try:

                # check the whether the order keeps the same
                
                # state_ind=ss.rankdata(State)-1
                # if not np.array_equal(state_ind, rank_index):
                #     # abandon the current simulation
                #     continue

                
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
                data_win[s]=price_v[int(max(State))]
                

                
                # second higest bidder to the difference
                order_ind=np.argsort(State)
                i_ed = order_ind[-2]
                i_rest =order_ind[:-2]
                temp_pos=(State[i_ed] - np.array(State[i_rest]))
                
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
                # third highest winning price (relative)
                
                if N>=3:
                    third_win_i[s] = price_v[State[order_ind[-3]]]
                else:
                    third_win_i[s] = np.nan
            except Exception as e:
                print(e)
                print('s:{},State:{},act:{}'.format(s,State,data_act[s,]))
            # Col_name=['ID', 'bidder_act', 'len_act','info_bidder_ID', 'bidder_state','bidder_price','ladder_norm',
            #   'real_num_bidder','win_norm', 'num_bidder','priority_people', 'price_norm','res_norm']
            temp_series=pd.Series([s,Data_act,len(Data_act),info_index,State,price_v[State],ladder,int(sum((State>0)*1)),price_v[int(max(State))],N,info_flag,price_v,res], index=Col_name )
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
    
