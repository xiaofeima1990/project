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
import copy
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


def map_integ_new(price_v,x_signal_i,x_low_bound,Update_bid,arg_data):
    i,high_bid,low_bid=arg_data

    exp_value = Update_bid.bid_vector_new(x_signal_i[:,i],x_low_bound,price_v,i)
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
    data_state=np.array(data_state)
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
    
    # I think it is still the entry threshold not the final posting price as the lower bound
    X_bar = Update_bid.lower_bound(r*np.ones(N))
    X_up = np.ones([1,N])*X_bar[0]
    X_up[0] = 4
    [x_signal,w_x]=signal_DGP_est(para,rng,N,0,X_bar,X_up,JJ)
    if x_signal.shape[0]<50:
        return 100000

    # re-order each bidder's bidding history
    # bidder_bid_history=[data_pos[int(ord_index[i])] for i in range(len(ord_index))]
    

    x_lower_bound=data_state[ord_index]

    # construct lower price bound and upper price bound
    # bid_low=[]
    
    # for ele in x_lower_bound:
    #     bid_low.append(price_v[int(ele)])
    # bid_low=[price_v[int(ele)] for ele in data_state]
    r_bar   = price_v[data_state[ord_index]]
    bid_low = r_bar
    bid_up  = (price_v[-1]+ladder)*np.ones(N)

    # sum_value=0

    # now I need to calculate empirical integ 
    # start = time.time()
    
    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])

    # use map to accelerate the speed

    # bid_v=price_v[data_state[ord_index]+1]


    map_func=partial(map_integ_new,price_v,x_signal,x_lower_bound,Update_bid)
    # i = 0.1.2.3... is the rank order for the participants!!!
    exp_value=list(map(map_func,zip(range(0,N),bid_up,bid_low))) 
    low_part =np.array([x[0] for x in exp_value])
    high_part=np.array([x[1] for x in exp_value])

    # winning bid no uppder bound constraints
    high_part[0]=0
    
    # sum together 
    sum_value=np.sum(low_part,axis=0)**0.5 + np.sum(high_part,axis=0)**0.5

    norm_var=Theta['comm_var']+Theta['priv_var']+Theta['epsilon_var']
    final_value=np.sum(sum_value)/(norm_var**0.5)
    
    # end = time.time()
    # print('return auction {} with # of bidder {} and result final_value {} '.format(tt,N,final_value))    
    # print('time expenditure: {}'.format(end - start))
    return final_value    
