# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 00:42:03 2018


@author: mgxgl

new modification :
    I believe inorder to fit the high dimentionality problems. the QMC may be 
    the better choice for me 
    the grid point should be either 
    * lattices
    * sparse grid
    
    make the integ part matrix
    
    
"""

import os 
import sys


sys.path.append('/storage/work/g/gum27/system/pkg/')

'''
install the package :
    eg. I am in the work directory and want to install on the pkg 
    pip install --target=system/pkg/ package_name

'''




import numpy as np
from simu import Simu
from Update_rule import Update_rule
from est import Est
from ENV import ENV
from scipy.optimize import minimize
import copy ,time,datetime
from collections import defaultdict,OrderedDict
from functools import partial
from scipy.stats import norm
#from scipy.stats import multivariate_normal
import multiprocessing
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
from functools import partial
from contextlib import contextmanager
import pickle as pk
import quantecon  as qe
from numpy import linalg as LA





Simu_para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)
   
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()




def signal_DGP_parallel(public_info,para,rng,N,JJ=15):
    

    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
    pub_mu = public_info[0]
    
    # random reservation ratio
    # r =  0.8 + 0.1*self.rng.rand() 
    r =  public_info[1]
    
    

#    x_signal=rng.multivariate_normal(MU.flatten(),SIGMA2,JJ)
    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
    info_index=public_info[3]
    
#    prob_x_signal=multivariate_normal.pdf(x_signal,MU.flatten(),SIGMA2)
    
    
    
    return [pub_mu,x_signal,w_x,info_index,r]

def signal_DGP(para,rng,N,JJ=400):


    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
#    pub_mu = public_info[0]
    
    # random reservation ratio
#    r =  public_info[1]
    
    
    # Cholesky Decomposition
    lambda_0,B=LA.eig(SIGMA2)
    lambda_12=lambda_0**(0.5)
    Sigma=B@np.diag(lambda_12)@LA.inv(B)
    
    # lattices 
    [xi_n,w_n]=qe.quad.qnwequi(int(JJ*N),np.zeros(N),np.ones(N),kind='R',random_state=rng)
    
    a_n= norm.ppf(xi_n)
    
    x_signal= Sigma@a_n.T +MU@np.ones([1,int(JJ*N)])
    x_signal= x_signal.T

#    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
#    info_index=public_info[3]
    
    
    return [x_signal,w_n]






def GMM_Ineq_parall(Theta0,DATA_STRUCT,d_struct):
    Theta={
    "comm_mu":Theta0[0],
    "priv_mu":Theta0[1],
    "epsilon_mu":Theta0[2],
    "comm_var":Theta0[3],
    "priv_var":Theta0[4],
    "epsilon_var":Theta0[5],
    }
    

    rng=np.random.RandomState(d_struct['rng_seed'])
    

    start = time.time()
    
    
    print('--------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
#    print('# of auctions: '+str(TT) )
    

    
    '''
    parallel programming with two levels
        data separating
        runing the estimation
    '''
    data_n=len(DATA_STRUCT)
    
    work_pool = ThreadPoolExecutor(max_workers=data_n)
    
    cpu_num=multiprocessing.cpu_count()
    #cpu_num=3
    
    auction_list=[]
    for Data_Struct in DATA_STRUCT:
        auction_list.append(work_pool.submit(partial(para_data_allo_1,Theta, int(cpu_num/data_n),rng,d_struct),Data_Struct).result())
    
    
    auction_result=np.mean(auction_list)
    
    end = time.time()
    
    print("object value : "+ str(auction_result) )
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
    
    ## save the parameters and objective value 
    
    with open('para.txt', 'w') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("%f\n" % auction_result)
    
    return auction_result


def para_data_allo_1(Theta,cpu_num, rng, d_struct, Data_struct):
    time.sleep(1)
    pub=Data_struct.pub_info[0,]
    
    print(" id: {} , is dealing the auction with {} bidder ".format(threading.get_ident(),pub[2]))
    
    
    
    
    JJ    =d_struct["JJ"]
    
    TT,T_end=Data_struct.data_act.shape
    TT = int(TT)
    T_end=int(T_end)
    print("the length of the auction is {}".format(TT))
    
    '''
    
    take the grid generation outsides
    
    '''
    
    # num of bidders in the auction
    N=int(pub[2])
    info_flag=pub[3]
    # setup the env info structure
    
    Env=ENV(N, Theta)

    if info_flag == 0 :
        para=Env.Uninform()
    else:
        para=Env.Info_ID()
    
    
    [x_signal,w_x]=signal_DGP(para,rng,N,JJ)
    
    results=[]
    
    
    func=partial(para_fun,para,info_flag,rng,T_end,int(JJ*N),x_signal,w_x)

    pool = ProcessPoolExecutor(max_workers=cpu_num)
    
    
    results= pool.map(func, zip(range(0,TT), Data_struct.data_act,Data_struct.data_state,Data_struct.pub_info))
    
    
    MoM=sum(results)/TT
    
    
    return MoM


def para_fun(para,info_flag,rng,T_end,JJ,x_signal,w_x, arg_data):
    
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
    
    price_v = np.linspace(r*pub_mu,pub_mu*1.2, T_end-10)
    price_v=np.append(price_v,np.linspace(1.24*pub_mu,pub_mu*1.8, 5))
    price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,5))
        
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
                
                
           
                
           


if __name__ == '__main__':
    
    
    # load the data

    simu_data = pk.load( open( "simu_data_est.pkl", "rb"))
    print("the total chunk of the input data is {}".format(len(simu_data)))
    
    # set up the hyper parameters
    rng_seed=789
    SS=25
    JJ=300
    
    
    d_struct={
            'rng_seed':rng_seed,
            'SS':SS,
            "JJ":JJ,
            }
    

    Theta=[10,1,0,0.8,1.2,0.8]
    
    start = time.time()
    now = datetime.datetime.now()
    print("------------------------------------------------------------------")
    print("optimization Begins at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("------------------------------------------------------------------")
    
    res = minimize(GMM_Ineq_parall, Theta, method='nelder-mead',args=(simu_data,d_struct)) 
    
    print("------------------------------------------------------------------")
    now = datetime.datetime.now()
    end = time.time()
    print("optimization ends at : "+ str(now.strftime("%Y-%m-%d %H:%M")))
    print("time spending is : %f minutes"  % ((end-start)/60) )
    print("------------------------------------------------------------------")
    print("\n\n\nFinal Output : \n")
    print(res)
    print(res.message)
    print(res.x)
            







#‘Nelder-Mead’ 
#‘Powell’
#‘CG’
#‘BFGS’
#‘Newton-CG’ 
#‘L-BFGS-B’ 
#‘TNC’ 
#‘COBYLA’ 
#‘SLSQP’ )
#‘trust-constr’
#‘dogleg’ 
#‘trust-ncg’ 
#‘trust-exact’ 
#‘trust-krylov’ 
