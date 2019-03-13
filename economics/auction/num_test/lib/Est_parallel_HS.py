# -*- coding: utf-8 -*-
"""
Created on Thur Feb 7 10:35:22 2019

@author: mgxgl
save the parallel running function

This is used for HS 

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


def map_E(N,h,Update_bid,x_signal):
    '''
    1 calcuate the expected value at each "round"
    for all bidders (active) as in Hong and Shum 2003
    This aims to do the smooth weighting simulation
    2 construct the "m"
    '''
    # calcualte the expected value at each "round"
    [E_post,E_value_list] = Update_bid.get_HS_drop_p(x_signal)

    # construct m in (35) Hong and Shum 2003
    # m denominator
    phi_v=np.array([])
    for kk in range(N-1):
        # loop from round k =0 to N-2 
        
        # consider the remaining bidder from 0 (highest) to N-kk -1 
        p_k   = E_post[kk]
        p_k_j = E_value_list[kk]

        diff  = (p_k_j - p_k )/h

        phi   = norm.cdf(diff)
        phi_v   = np.append(np.prod(phi),phi_v)

      
    m_denominator = np.prod(phi_v)
    
    # m nominator from last round to the first round 
    # I have to match with the upper and lower bound 
    m_nominator = m_denominator * E_post[::-1]

    return [m_nominator,m_denominator]




def para_fun_est(Theta,rng,xi_n,h,arg_data):
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
    X_up = np.ones([1,N])*3
    x_signal=signal_DGP_est(para,rng,N,0,X_bar,X_up,xi_n)
    if x_signal.shape[0]<15:
        print("t is {}".format(tt) )
        return 100000


    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])

    # now I need to calculate empirical integ 
    # start = time.time()

    # 1 calculate the complicated expected value at each "round" for all remaining bidders
    map_func=partial(map_E,N,h,Update_bid)
    m_k_s=list(map(map_func,x_signal))
    m_k_s_1 = np.array([x[0] for x in m_k_s])
    m_k_s_2 = np.array([x[1] for x in m_k_s])

    # take mean for m_k_s_1 and m_k_s_2 to calculate the m_k
    de_PT = np.mean(m_k_s_2)
    mk_v = np.mean(m_k_s_1,axis=0)
    
    # construct price vector for the posting price
    post_price  = price_v[data_state[ord_index]]

    # personally I think if I multiply de_PT, the objective function would be very small
    # 
    low_1     =  post_price  - mk_v/de_PT
    low_sum = np.square(low_1)
    sum_value = np.nansum(low_sum)
    sum_value =sum_value/0.01
    
    return sum_value
 