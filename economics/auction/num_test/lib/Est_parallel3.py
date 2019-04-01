# -*- coding: utf-8 -*-
"""
Created on Thur Mar 21 08:35:22 2019

@author: mgxgl
save the parallel running function

# --------------03-26-2019-------------------#
1 modfiy for (34) and (35) in Hong and Shum 2003
  only consider the last two bidders sequence
2 construct the MLE 


"""

from functools import partial
from collections import defaultdict,OrderedDict
import time,datetime
import numpy as np
from Update_rule3 import Update_rule
from ENV import ENV
from Util import *
import copy
import scipy.stats as ss



def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)


def cal_MLE1(state_p_log,bid_post_log,no_flag,Update_bid,threshold,ladder):
    '''
    MLE of the first test 
    this is old version that use the probability of 
    Prob(Xi in [xi_low, xi_up] | Omega_it xj in [xj_low,xj_up])
    
    1. calculate the X range support 
    2. calculate the prob
    threshold : [r,r,r,...]  
    '''
    
    [low_support,high_support] = Update_bid.support_x(state_p_log,bid_post_log,threshold,no_flag,ladder)
    # low and high support clean
    high_support[-2] = low_support[-2] if low_support[-2]>high_support[-2] else high_support[-2]
            
    # deal with the truncated part 
    # low : r,r,r... x_2nd 
    # high : x_2nd, ....x_2nd, infty
    x2nd=high_support[-2]
    high_support[-1]=10
    log_Prob                   = Update_bid.MLE_X_new_omega(low_support,high_support,threshold,x2nd)

    
    #print(log_Prob)
    # aim is minimizing
    return -log_Prob

def cal_MLE2(state_p_log,bid_post_log,no_flag,Update_bid,threshold,ladder):
    '''
    MLE of the second test 
    Prob(Xi not in [xi_low, xi_up] | Omega_it xj in [xj_low,xj_up])
    doing minimize directly
    calculate the X range support 
    threshold : [r,r,r,...]  
    '''
    
    [low_support,high_support] = Update_bid.support_x(state_p_log,bid_post_log,threshold,no_flag,ladder)
    # low and high support clean
    high_support[-2]           = low_support[-2] if low_support[-2]>high_support[-2] else high_support[-2]
      
    x2nd=high_support[-2]
    high_support[-1]=10
    log_Prob                   = Update_bid.MLE_X_new_omega2(low_support,high_support,threshold,x2nd)

    
    #print(log_Prob)
    return log_Prob

def cal_MLE3(state_p_log,bid_post_log,no_flag,Update_bid,threshold,ladder):
    '''
    calculate the likelihood function like Karl said. 
    Prob_Xi (Xi in [X_low, X_up] | Xi > gamma) 
    I just realized that this has been used in the Hong Shum 2003

    '''

    [low_support,high_support] = Update_bid.support_x(state_p_log,bid_post_log,threshold,no_flag,ladder)
    # low and high support clean
    high_support[-2]           = low_support[-2] if low_support[-2]>high_support[-2] else high_support[-2]
    high_support[-1]=10
    log_Prob                   = Update_bid.MLE_X_new_karl(low_support,high_support,threshold)

    return log_Prob
      

def cal_E_moment(N,h,state_p_log,bid_post_log,no_flag,Update_bid,threshold,ladder):
    '''
    calculate the Expected pivotal function for each bidder within auction t
    This is the updated version for my moment inequality estimation
    1. get the lower and upper bound for each bidder from the bidding history Omega
    2. fix X_J support, and calculate the truncated prob for xi>gamma, XJ in [X_low,X_up] (each xj)
    3. Once get the random X matrix and w weighting vector, We also know the [xi_low,xi_up]. We
       do the calculation for expectation
    4. construct the "m" as in hong and shum 2003 (smooth objective function) (34)
    5. use the upper and lower bidding price to calculate the moment inequalities as before  
    '''
    [low_support,high_support]     = Update_bid.support_x(state_p_log,bid_post_log,threshold,no_flag,ladder)

    # generate the truncated random vectors X > gamma
    low_bound=threshold
    up_bound= 10*np.ones(N)
    
    flag=1
    loop_flag=True
    while flag<5 and loop_flag:
        [x_v,w_v]              = Update_bid.GHK_simulator(0,low_bound,up_bound,0,S=300+500*flag) # x_v is N * S 
    
        # I think I need to add a function that select the order information that I have. 
        [x_v,w_v]      = order_selection(x_v.T,w_v.T) # input should be S * N 
        if x_v.shape[0] >100 and flag<5:
            loop_flag=False
        if x_v.shape[0] <100 and flag>5:
            return np.nan*np.ones(N)
        
        flag+=1


    # calculate the conditional expected bidding function Ebeta(vi|xi,xj)
    # also we need to use the order of the bidding functions
    # i=0 lowest i=N highest
    map_func=partial(map_E,N,h,state_p_log,no_flag,ladder,Update_bid)
    m_k_s=list(map(map_func,x_v))
    m_k_s_1 = np.array([x[0] for x in m_k_s])
    m_k_s_2 = np.array([x[1] for x in m_k_s])

    # take mean for m_k_s_1 and m_k_s_2 to calculate the m_k
    de_PT = np.mean(m_k_s_2)
    mk_v = np.mean(m_k_s_1,axis=0)
    

    return mk_v/de_PT


def map_E(N,h,state_p_l_bound,no_flag,ladder,Update_bid,x_signal):
    '''
    1 calcuate the expected value at each "round"
    for all bidders (active) as in Hong and Shum 2003
    This aims to do the smooth weighting simulation
    2 construct the "m" as in hong and shum 2003 (smooth objective function) (34)
    '''
    # calcualte the expected value at each "round"
    [E_post,E_value_list] = Update_bid.post_E_value(state_p_l_bound,no_flag,ladder,x_signal)

    # construct m in (35) Hong and Shum 2003
    # m denominator
    phi_v=np.array([])
    for kk in range(N-1):
        # loop from round k =0 to N-2 
        
        # consider the remaining bidder from 0 (highest) to N-kk -1 
        p_k   = E_post[kk]
        p_k_j = E_value_list[kk]

        diff  = (p_k_j - p_k )/h

        phi     = ss.norm.cdf(diff)
        phi_v   = np.append(np.prod(phi),phi_v)
      
    m_denominator = np.prod(phi_v)
    
    # m nominator from last round to the first round 
    # I have to match with the upper and lower bound 
    m_nominator = m_denominator * E_post 

    return [m_nominator,m_denominator]



def para_fun_est(Theta,rng,d_struct,arg_data,METHOD_flag=1):
    '''
    main function for calculation
    METHOD_flag: decide to use moment estimation or MLE
                 1-> MLE      2-> MoM 

    '''
    MLE_flag=d_struct['MLE_choice']
    model_flag= d_struct['model_flag']
    h = d_struct['h']
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
    iden_index=np.zeros(N)
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
    X_bar = Update_bid.threshold_simple(r*np.ones([1,N]))


    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])

    # time spend
    # start = time.time()

    # re-order each bidder's bidding history
    bidder_bid_history=[data_pos[int(ord_index[i])] for i in range(len(ord_index))]
    bid_v   = data_state[ord_index]

    low_state=np.zeros((N,N))

    # get the bidder's lower bound state for calculation
    # N * N diag is the bidder's own previous bidding
    for i in range(0,N):
        temp_s=[]
        for j in range(0,N):
            try:
                bid_post=bidder_bid_history[j][1]
            
                if bid_post[0] > bid_v[i]:
                    temp_s.append(0)
                else: 
                    temp_p=[x for x in bid_post if x < bid_v[i] ]
                    temp_p.sort()
                    if len(temp_p)>=1:
                        temp_s.append(temp_p[-1])
                    else:
                        temp_s.append(0)
            except Exception as e:
                print(e)
                print(data_pos)
                print(temp_p)
                print(bid_v[i])
                temp_s.append(0)
                print('this is number ',tt)
                input('wait for check')
                
        low_state[i,:] = temp_s
        low_state[i,i] = bid_v[i]
    low_state=low_state.astype(int)
    no_flag=(low_state<1)*1
    state_p_history= price_v[low_state]

    if model_flag==0:
        # calculate the moment inequality condition
        low_price_bound=np.log(price_v[bid_v])[::-1]
        up_price_bound=np.log(np.exp(low_price_bound[-1])+ladder) * np.ones(N)
        E_XV=cal_E_moment(N,h,np.log(state_p_history),np.log(price_v[bid_v]),no_flag,Update_bid,X_bar,ladder)

        low_1     =  low_price_bound  - E_XV
        high_1    =  up_price_bound   - E_XV
        low_sum = np.square((low_1>0)*1*low_1)
        high_sum = np.square((high_1<0)*1*high_1)
        high_sum[-1]=0

        sum_value = np.nansum(low_sum) + np.nansum(high_sum)
        result_value = sum_value/0.001
        # print(result_value)

    else:
        # calculate the MLE 
        if MLE_flag == 1:
            log_prob=cal_MLE1(np.log(state_p_history),np.log(price_v[bid_v]),no_flag,Update_bid,X_bar,ladder)        
        elif model_flag==2:
            log_prob=cal_MLE2(np.log(state_p_history),np.log(price_v[bid_v]),no_flag,Update_bid,X_bar,ladder)
        else: 
            log_prob=cal_MLE3(np.log(state_p_history),np.log(price_v[bid_v]),no_flag,Update_bid,X_bar,ladder)
        
        result_value = log_prob  


    return result_value
 