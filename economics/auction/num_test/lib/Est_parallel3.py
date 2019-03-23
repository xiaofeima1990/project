# -*- coding: utf-8 -*-
"""
Created on Thur Mar 21 08:35:22 2019

@author: mgxgl
save the parallel running function

modfiy for (34) and (35) in Hong and Shum 2003

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


def cal_Prob(state_p_log,bid_post_log,no_flag,Update_bid,threshold,ladder):
    '''
    # calculate the X range support 
    '''
    # calcualte the expected value at each "round"
    [x_v,U_v,w_v]              = Update_bid.GHK_simulator(threshold,10,0)
    [low_support,high_support] = Update_bid.support_x(state_p_log,bid_post_log,no_flag,ladder)

    log_Prob                   = Update_bid.prob_X_trunc(low_support,high_support,threshold,x_v,w_v)

    return log_Prob


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
    low_state=low_state.astype(int)
    no_flag=(low_state<1)*1
    state_p_history= price_v[low_state]
    # calculate the MLE
    log_prob=cal_Prob(np.log(state_p_history),np.log(price_v[bid_v]),no_flag,Update_bid,X_bar,ladder)
    return -log_prob
 