# -*- coding: utf-8 -*-
"""
Created on Thur Feb 7 10:35:22 2019

@author: mgxgl
save the parallel running function

modfiy for (34) and (35) in Hong and Shum 2003

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


def map_integ_new(price_v,x_signal_i,low_state,high_bound,Update_bid,arg_data):
    i,bid,high_bid,low_bid=arg_data
    # calculate lower bound
    exp_value1 = Update_bid.bid_vector_low(x_signal_i[:,i],bid,low_state[i],price_v,i)

    (exp_value2,w_n2) = Update_bid.bid_vector_high(x_signal_i[:,i],high_bound,price_v,i)

    # count the criterion
    low_case  = 1*(low_bid  <= exp_value1) # this lower bound should be one of the criterion
    # high_case = 1*(high_bid >= exp_value2)
    low_case=low_case.flatten()
    # question ~~~ how can I add w_n2
    final_w=w_n2*low_case
    
    return (exp_value2.flatten(),final_w)

def map_integ_final(arg_data):
    high_bid,low_bid,exp_value = arg_data
    exp_value_S= np.mean(exp_value)
    
    low_1     =  low_bid  - exp_value_S
    high_1    =  high_bid - exp_value_S
    low_sum = np.square((low_1>0)*1*low_1)
    high_sum = np.square((high_1<0)*1*high_1)
    return (low_sum,high_sum)

def map_E(N,h,state_p_l_bound,Update_bid,x_signal):
    '''
    1 calcuate the expected value at each "round"
    for all bidders (active) as in Hong and Shum 2003
    This aims to do the smooth weighting simulation
    2 construct the "m"
    '''
    # calcualte the expected value at each "round"
    [E_post,E_value_list] = Update_bid.post_E_value(state_p_l_bound,xi_v)

    # construct m in (35) Hong and Shum 2003
    # m denominator
    phi_v=np.array([])
    for kk in range(N-1):
        # loop from round k =0 to N-2 
        
        # consider the remaining bidder from 0 (highest) to N-kk -1 
        p_k   = E_post[kk]
        p_k_j = E_value_list[kk]

        diff  = (p_k_j - p_k )/h

        phi   = norm.pdf(diff)
        phi_v   = np.append(np.prod(phi),phi_v)

      
    m_denominator = np.prod(phi_v)
    
    # m nominator from 0 to N-2 round 
    m_nominator = m_denominator * E_post

    return [m_nominator,m_denominator]








def para_fun_est(Theta,rng, ,arg_data):
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

    

    # add whether it is informed or not informed  
    Update_bid.setup_para(i_id)
    
    # I think it is still the entry threshold not the final posting price as the lower bound
    X_bar = Update_bid.bound(r*np.ones([1,N]))
    # Why I need up, I do not need it 
    X_up = np.ones([1,N])*4
    x_signal=signal_DGP_est(para,rng,N,0,X_bar,X_up,xi_n)




    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])
    # construct price vector for the posting price
    post_price  = price_v[data_state[ord_index]]

    # now I need to calculate empirical integ 
    # start = time.time()

    low_state=np.zeros((N,N))

    # get the bidder's lower bound state for calculation
    for i in range(0,N):
        for j in range(0,N):
            try:
                bid_post=bidder_bid_history[j][1]
            
                if bid_post[0] > bid_v[i]:
                    temp_s.append(0)
                else: 
                    temp_p=[x for x in bid_post if x < bid_v[i] ]
                    temp_p.sort()
                    temp_s.append(temp_p[-1])
            except Exception as e:
                print(e)
                print(data_pos)
                print(temp_p)
                print(bid_v[i])
                temp_s.append(0)
                print('this is number ',tt)
                input('wait for check')
                
        low_state[i,:] = temp_s

    state_p_l_bound= price_v[low_state]
    # 1 calculate the complicated expected value at each "round" for all remaining bidders
    map_func=partial(map_E,N,h,state_p_l_bound,Update_bid)
    m_k_s=list(map(map_func,x_signal))
    m_k_s_1 = np.array([x[0] for x in m_k_s])
    m_k_s_2 = np.array([x[1] for x in m_k_s])

    # take mean for m_k_s_1 and m_k_s_2 to calculate the m_k
    de_PT = np.mean(m_k_s_2)
    mk_v = np.mean(m_k_s_1,axis=1)
    
    # lower bound and upper bound 
    low_bound   = price_v[data_state[ord_index]]
    up_bound    = low_bound[0]*np.ones(N)


    low_1     =  low_bound*de_PT  - exp_value_S
    high_1    =  up_bound*de_PT - exp_value_S
    low_sum = np.square((low_1>0)*1*low_1)
    high_sum = np.square((high_1<0)*1*high_1)
    high_sum[0]=0
    low_sum[1] =low_sum[1]*N 
    high_sum[1] = high_sum[1] * N 
    sum_value = np.sum(low_sum)/(2*N)+np.sum(high_sum)/(2*N)
    return sum_value
 