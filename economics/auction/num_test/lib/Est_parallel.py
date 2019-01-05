# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 18:35:22 2018

@author: mgxgl
save the parallel running function

modify the private part
where mu_ai = a_1*i  ; var_ai = a_2*i 


"""
from functools import partial
from collections import defaultdict,OrderedDict
import time,datetime
import numpy as np
from Update_rule import Update_rule
from ENV import ENV
from Util import *


def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)


def map_integ(price_v,x_signal_i,s_state,Update_bid,arg_data):
    i,bid,low_bid,high_bid=arg_data
    state=s_state[i]

    exp_value = Update_bid.bid_vector(x_signal_i[:,i],bid,state,price_v,i)

    low_case  = low_bid  - exp_value
    high_case = high_bid - exp_value

    low_sum = np.square((low_case>0)*1*low_case)
    high_sum = np.square((high_case<0)*1*high_case)
    return (low_sum,high_sum)





def para_fun_est(Theta,rng,JJ,arg_data):
    tt,data_state,data_pos,price_v,pub_info=arg_data
    info_flag=pub_info[3]
    N        =int(pub_info[2])

    ord_index=np.argsort(data_state)[::-1]
    info_v=np.ones(N)
    if info_flag-1 >=0:
        info_v[info_flag] = 0

    r     =pub_info[-1]
    Env=ENV(N, Theta,r,ord_index,info_v)
    para=Env.info_struct()

    # if info_flag == 0 :
    #    para=Env.Uninform()
    # else:
    #    para=Env.Info_ID()


    
    ladder=pub_info[0]
    Update_bid=Update_rule(para,r)

    

    JJ=JJ+50*N
    [x_signal,w_x]=signal_DGP_est(para,rng,N,0,r,JJ)


    data_pos.sort()


    state_temp=np.zeros((N,N))

     # get the bidders state for calculation
    for i in range(0,len(data_state)):
        flag_select=np.ones(N)
        flag_select[i]=0
        select_flag=np.nonzero(flag_select)[0].tolist()

        state_temp[i,0]=data_state[i]
        
        temp_s=[]
        for j in select_flag:
            try:
                bid_post=data_pos[j][1]
                
                
                if bid_post[0] > data_state[i]:
                    temp_s.append(0)
                else: 
                    temp_p=[x for x in bid_post if x < data_state[i] ]
                    temp_p.sort()
                    temp_s.append(temp_p[-1])
            except Exception as e:
                print(e)
                print(data_pos)
                print(temp_p)
                print(data_state[i])
                temp_s.append(0)
                print('this is number ',tt)
                input('wait for check')
                
        state_temp[i,1:] = temp_s


    # for the expected value of each bidders
    
    
    bid_low=[]
    
    for ele in data_state:
        bid_low.append(price_v[int(ele)])
    # bid_low=[price_v[int(ele)] for ele in data_state]
    bid_up =(price_v[-1]+ladder)*np.ones(N)

    sum_value=0
    # now I need to calculate empirical int 
    start = time.time()
    
    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])

    # use map to accelerate the speed
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
    final_value=np.sum(sum_value)/(Theta['comm_var']**0.5)
    
    end = time.time()
    
    print('return auction {} with # of bidder {} and result final_value {} '.format(tt,N,final_value))    
    
    print('time expenditure')
    print(end - start)
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
    
            
#    print('start calculating auction {} with # of bidder {}'.format(tt,N))
    
 
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
                
def para_fun_old(para,info_flag,rng,T_end,JJ,x_signal,w_x, arg_data):
    
    tt,data_act,data_state,pub_info=arg_data
    
   # print('start calculating auction {} with # of bidder {}'.format(tt,N))
    
    # info_flag=pub_info[3]
    
#    Env=ENV(N, Theta)
#
#    if info_flag == 0 :
#        para=Env.Uninform()
#    else:
#        para=Env.Info_ID()

    Update_bid=Update_rule(para)
    
#        [pub_mu,x_signal,w_x,info_index,r] = signal_DGP_parallel(pub_info,para,rng,J)
    
    pub_mu=pub_info[0]
    r     =pub_info[1]
    N     =int(pub_info[2])
    
            
    print('start calculating auction {} with # of bidder {}'.format(tt,N))
    
 
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
    exp_value=np.zeros([JJ,N])
    low_case =np.zeros([JJ,N])
    up_case  =np.zeros([JJ,N])
    for i in range(0,N):
        bid=int(max(state_temp[i,:]))+1
        ss_state=[int(x) for x in state_temp[i,:].tolist()]
#        for j in range(0,JJ):
#            exp_value[j,i] =Update_bid.real_bid(x_signal[j,i],bid,ss_state,price_v)[0][0]
        fun_bid=lambda xi :Update_bid.real_bid(xi,bid,ss_state,price_v)
        temp=list(map(fun_bid,x_signal[:,i]))
        temp=np.array([ele[0][0] for ele in temp])
#        temp=np.array([Update_bid.real_bid(xi,bid,ss_state,price_v)[0][0] for xi in x_signal[:,i]])
        exp_value[:,i]=temp.flatten()
            
        low_case[:,i]=bid_low[i]-exp_value[:,i]
        up_case[:,i] =bid_up[i] -exp_value[:,i]
    
    
    index_win=np.argmax(data_state)
    up_case[index_win]=0
    
    
    sum_value=np.sum(np.square((low_case>0)*1*low_case),axis=1)**0.5 + np.sum(np.square((up_case<0)*1*up_case),axis=1)**0.5
    sum_value=sum_value * w_x
    final_value=np.sum(sum_value)
    end = time.time()
    
    print('return auction {} with # of bidder {} and result final_value {} '.format(tt,N,final_value))    
    
    print('time expenditure')
    print(end - start)
    return final_value
