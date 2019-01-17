# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 18:35:22 2018

@author: mgxgl
save the parallel running function

modify the private part--no
where mu_ai = a_1*i  ; var_ai = a_2*i 
remember the price should take log form

I should keep the setup
where mu_ai = a_1  ; var_ai = a_2

I just realied that my estimation moment has some problems 
modify the map_integ to take average inside the integ
"""
from functools import partial
from collections import defaultdict,OrderedDict
import time,datetime
import numpy as np
from Update_rule import Update_rule
from ENV import ENV
from Util import *
import scipy.stats as ss



def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)


def map_integ(price_v,x_signal_i,s_state,Update_bid,arg_data):
    i,bid,high_bid,low_bid=arg_data
    state=s_state[i]

    exp_value = Update_bid.bid_vector(x_signal_i[:,i],bid,state,price_v,i)
    # I just realized that I have to take integration inside 
    # like Hong and Shum 2003 SNLS, because x_signal is unkown and simulated. 
    # not like CT 2009 , their X can be observed

    exp_value_M = np.mean(exp_value)

    low_case  = low_bid  - exp_value_M
    high_case = high_bid - exp_value_M

    low_sum = np.square((low_case>0)*1*low_case)
    high_sum = np.square((high_case<0)*1*high_case)
    return (low_sum,high_sum)





def para_fun_est(Theta,rng,JJ,arg_data):
    tt,data_state,data_pos,price_v,pub_info=arg_data
    info_flag=pub_info[3]
    N        =int(pub_info[2])
    # finally I realized that my previous thought has big problem, what I want is actually the rank sequence not the sorted order. 
    # bug bug we should use np.argsort(data_state) not np.argsort(data_state)[::-1]
    # No no rank order !
    # ord_index=np.argsort(data_state)    # order the bidder's bidding value, highest has high order index! 
    #                                     # ord_index=np.argsort(data_state)[::-1] descedning order
    # rank_index=ss.rankdata(data_state)-1
    # wait still, I can use rank order to dervie the dropout price. 

    # order index to order from highest to lowest 
    ord_index=np.argsort(data_state)[::-1] 
    # index for generating the bidder identity make everyone the same
    iden_index=np.ones(N)
    info_v=np.ones(N)
    i_id=0
    if info_flag-1 >=0:
        info_v[info_flag] = 0
        if info_v[0] == 1:
            i_id = 0
        else:
            i_id = 1
    r     =pub_info[-1]

    
    Env=ENV(N, Theta)
    # argument for info_struct info_flag,ord_index,res
    para=Env.info_struct(info_v,iden_index,r)

    
    ladder=pub_info[0]
    Update_bid=Update_rule(para,r)

    

    JJ=JJ+100*N
    # add whether it is informed or not informed  
    Update_bid.setup_para(i_id)
    r_bar=price_v[ord_index]
    X_bar = Update_bid.lower_bound(r_bar)
    
    [x_signal,w_x]=signal_DGP_est(para,rng,N,0,X_bar,JJ)
    if x_signal.shape[0]<50:
        return 100000

    # re-order 
    data_pos.sort()
    bidder_bid_history=data_pos[ord_index]
    



    state_temp=np.zeros((N,N))

    #  # get the bidders state for calculation
    # for i in range(0,N):
    #     flag_select=np.ones(N)
    #     flag_select[i]=0
    #     select_flag=np.nonzero(flag_select)[0].tolist()

    #     state_temp[i,0]=data_state[i]
        
    #     temp_s=[]
    #     for j in select_flag:
    #         try:
    #             bid_post=data_pos[j][1]
                
                
    #             if bid_post[0] > data_state[i]:
    #                 temp_s.append(0)
    #             else: 
    #                 temp_p=[x for x in bid_post if x < data_state[i] ]
    #                 temp_p.sort()
    #                 temp_s.append(temp_p[-1])
    #         except Exception as e:
    #             print(e)
    #             print(data_pos)
    #             print(temp_p)
    #             print(data_state[i])
    #             temp_s.append(0)
    #             print('this is number ',tt)
    #             input('wait for check')
                
    #     state_temp[i,1:] = temp_s




    # for the expected value of each bidders
    
    
    bid_low=[]
    
    for ele in data_state:
        bid_low.append(price_v[int(ele)])
    # bid_low=[price_v[int(ele)] for ele in data_state]
    bid_up =(price_v[-1]+ladder)*np.ones(N)

    sum_value=0
    # now I need to calculate empirical int 
    # start = time.time()
    
    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])

    # use map to accelerate the speed
    bid_v=[]
    ss_state_v=[]
    for i in range(0,N):
        bid_v.append(int(max(state_temp[i,:]))+1)
        ss_state_v.append([int(x) for x in state_temp[i,:].tolist()])
    
    # censer_prob=[1-ss.norm.cdf(X_bar,ele[0],ele[1]) for ele in zip(para.xi_mu,para.xi_sigma2)]
    map_func=partial(map_integ,price_v,x_signal,ss_state_v,Update_bid)
    # ss_state_v how to load the right part 
    exp_value=list(map(map_func,zip(range(0,N),bid_v,bid_up,bid_low))) 
    low_part =np.array([x[0] for x in exp_value])
    high_part=np.array([x[1] for x in exp_value])
    # I believe there exist some problem for 
    # the winning bidder upper case Need more time to debug
    index_win=np.argmax(data_state)
    # high_part[index_win,:]=0
    high_part[index_win]=0
    
    # dimension problem
    sum_value=np.sum(low_part,axis=0)**0.5 + np.sum(high_part,axis=0)**0.5
    # sum_value=sum_value * w_x / sum(w_x)
    norm_var=Theta['comm_var']+Theta['priv_var']+Theta['epsilon_var']
    final_value=np.sum(sum_value)/(norm_var**0.5)
    
    # end = time.time()
    # print('return auction {} with # of bidder {} and result final_value {} '.format(tt,N,final_value))    
    # print('time expenditure: {}'.format(end - start))
    return final_value    


def para_fun(para,info_flag,rng,T_end,JJ,x_signal,w_x, arg_data):
    
    tt,data_act,data_state,pub_info=arg_data
    data_state=data_state[data_state!=-1]
   # print('start calculating auction {} with # of bidder {}'.format(tt,N))
    
    # info_flag=pub_info[3]
    
    #    Env=ENV(N, Theta)
    #
    #    if info_flag == 0 :
    #        para=Env.Uninform()
    #    else:
    #        para=Env.Info_ID()

    Update_bid=Update_rule(para)
    
    
    pub_mu=pub_info[0]
    r     =pub_info[1]
    N     =int(pub_info[2])
    ladder=pub_info[4]
    
            
    #print('start calculating auction {} with # of bidder {}'.format(tt,N))
    
 
    can_bidder_lists=list(list_duplicates(data_act))
    can_bidder_lists=[x for x in can_bidder_lists if x[0] != -1 ]
    can_bidder_lists.sort()
    

   
    # clean the data
    cc_bidder_list=[]
    for i in range(0,N):
        try:
            if can_bidder_lists[i][0]==i:
                can_temp=[x+1 for x in can_bidder_lists[i][1]]
                can_temp.append(0)
                can_temp.sort()
                cc_bidder_list.append((i,can_temp))
            else:
                cc_bidder_list.insert(i,(i,[0]))
                can_bidder_lists.insert(i,(i,[0]))
        except Exception as e:
            print(e)
            print("tt={} and N = {} ".format(tt,N))
            return np.nan
    
    
    state_temp=np.zeros((N,N))
    
    price_v = np.array(range(1,T_end+2))*ladder + pub_mu*r
    price_v = np.append(pub_mu*r,price_v)
    # get the bidders state for claculation
    for i in range(0,len(data_state)):
        flag_select=np.ones(N)
        flag_select[i]=0
        select_flag=np.nonzero(flag_select)[0].tolist()

        state_temp[i,0]=data_state[i]
        
        temp_s=[]
        for j in select_flag:
            bid_post=cc_bidder_list[j][1]
            
            temp_p=[x for x in bid_post if x < data_state[i] ]
            temp_p.sort()
            temp_s.append(temp_p[-1])
        
        state_temp[i,1:] = temp_s
        
        
    # for the expected value of each bidders
    
    
    bid_low=[]
    
    for ele in data_state:
        bid_low.append(price_v[int(ele)])

    bid_up =price_v[int(max(data_state)+1)]*np.ones(N)
    
    
    
    sum_value=0
    # now I need to calculate empirical int 
    start = time.time()
    
    

    # change this into function and use map (try) to run all bidder's simultaneously 



    bid_v=[]
    ss_state_v=[]
    for i in range(0,N):
        bid_v.append(int(max(state_temp[i,:]))+1)
        ss_state_v.append([int(x) for x in state_temp[i,:].tolist()])
    map_func=partial(map_integ,price_v,x_signal,ss_state_v,Update_bid)
    # ss_state_v how to load the right part 
    exp_value=list(map(map_func,zip(range(0,N),bid_v,bid_up,bid_low))) 
    low_part=np.array([x[0] for x in exp_value])
    high_part=np.array([x[1] for x in exp_value])
    # I believe there exist some problem for 
    # the winning bidder upper case Need more time to debug
    index_win=np.argmax(data_state)
    high_part[index_win,:]=0
    
    # dimension problem
    sum_value=np.sum(low_part,axis=0)**0.5 + np.sum(high_part,axis=0)**0.5
    sum_value=sum_value * w_x
    final_value=np.sum(sum_value)
    
    end = time.time()
    
    print('return auction {} with # of bidder {} and result final_value {} '.format(tt,N,final_value))    
    
    print('time expenditure')
    print(end - start)
    return final_value
                
