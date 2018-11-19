# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 10:58:20 2018

@author: mgxgl

main program for running the estimation test


"""


import numpy as np
from simu import Simu
from Update_rule import Update_rule
from est import Est
from ENV import ENV
from scipy.optimize import minimize
import copy ,time,datetime
from collections import defaultdict,OrderedDict
from functools import partial
from scipy.stats import multivariate_normal
import multiprocessing
from functools import partial
from contextlib import contextmanager
import pickle as pk


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
    return ((key,locs) for key,locs in tally.items() if len(locs)>1)
   
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()




def signal_DGP_parallel(public_info,para,rng,N,JJ=6000):
    

    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
    pub_mu = public_info[0]
    
    # random reservation ratio
    # r =  0.8 + 0.1*self.rng.rand() 
    r =  public_info[1]
    
    

    x_signal=rng.multivariate_normal(MU.flatten(),SIGMA2,JJ)
    
    info_index=public_info[3]
    
#    prob_x_signal=multivariate_normal.pdf(x_signal,MU.flatten(),SIGMA2)
    
    
    
    return [pub_mu,x_signal,info_index,r]



def GMM_Ineq_parall(Theta0,Data_struct,d_struct):
    Theta={
    "comm_mu":Theta0[0],
    "priv_mu":Theta0[1],
    "epsilon_mu":Theta0[2],
    "comm_var":Theta0[3],
    "priv_var":Theta0[4],
    "epsilon_var":Theta0[5],
    }
    
    ## numbers
    
    T_end =d_struct['T_end']
    J     =d_struct["JJ"]
    
    TT=d_struct['T'] # number of auctions in the data
    info_flag=d_struct['info_flag']
    

    rng=np.random.RandomState(d_struct['rng_seed'])
    

    start = time.time()
    
    MoM=0
    
    print('--------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
    print('# of auctions: '+str(TT) )

    # parallel programming      
    results=[]
    func=partial(para_fun,Theta,info_flag,rng,T_end,J)
    with poolcontext(processes=5) as pool:
        results= pool.map(func, zip(range(0,TT), Data_struct.data_act,Data_struct.data_state,Data_struct.pub_info))
                
    MoM=sum(results)        

    end = time.time()
    
    print("object value : "+ str(MoM/TT) )
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
    
    ## save the parameters and objective value 
        
    with open('para.txt', 'w') as f:
        for item in Theta0:
            f.write("%f\t" % item)
            
        f.write("%f\n" % MoM/TT)
            
    return MoM/TT


def para_fun(Theta,info_flag,rng,T_end,J,arg_data):
        tt,data_act,data_state,pub_info=arg_data
        
        # num of bidders in the auction
        N=pub_info[2]
            # setup the env info structure
        Env=ENV(N, Theta)
        if info_flag == 0 :
            para=Env.Uninform()
        else:
            para=Env.Info_ID()
        Update_bid=Update_rule(para)
        
        [pub_mu,x_signal,info_index,r] = signal_DGP_parallel(pub_info,para,rng,J)
        print(tt)
        can_bidder_lists=list(list_duplicates(data_act))
        can_bidder_lists=[x for x in can_bidder_lists if x[0] != -1 ]
        can_bidder_lists.sort()
        # clean the data
        cc_bidder_list=[]
        for i in range(0,N):

            if can_bidder_lists[i][0]==i:
                can_temp=[x+1 for x in can_bidder_lists[i][1]]
                can_temp.append(0)
                can_temp.sort()
                cc_bidder_list.append((i,can_temp))
            else:
                cc_bidder_list.insert(i,(i,[0]))
                can_bidder_lists.insert(i,(i,[0]))
            
                
                    
                
        
        
        state_temp=np.zeros((N,N))
        
        price_v = np.linspace(pub_info[1]*pub_mu,pub_mu*1.2, T_end-10)
        price_v=np.append(price_v,np.linspace(1.24*pub_mu,pub_mu*1.8, 5))
        price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,5))
            
        # get the bidders state for claculation
        for i in range(0,len(data_state)):
            flag_select=[1,1,1]
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

        bid_up =price_v[int(max(data_state)+1)]*np.ones(3)
        
        
        
        
        sum_value=0
        # now I need to calculate empirical int 
        for j in range(0,J):
            
            exp_value=np.zeros(3)
            low_case =np.zeros(3)
            up_case  =np.zeros(3)
            
            
            for i in range(0,N):
                bid=int(max(state_temp[i,:]))+1
                ss_state=[int(x) for x in state_temp[i,:].tolist()]
                result = Update_bid.real_bid(x_signal[j,i],bid,ss_state,price_v)
                
                exp_value[i]=result[0][0]
            
            # calcuate the first part b-exp<= 0 
            low_case=bid_low-exp_value
            up_case =bid_up-exp_value
            index_win=np.argmax(data_state)
            up_case[index_win]=0
        
            # new
            sum_value=sum_value+sum(np.square((low_case>0)*1*low_case)) + sum(np.square((up_case<0)*1*up_case))
            
            # old
#            exp_value=sum(np.square((low_case>0)*1*low_case)) + sum(np.square((up_case<0)*1*up_case))
#            exp_value=exp_value*prob_x_signal[j] + exp_value
            
        return sum_value/J
                
                
           


if __name__ == '__main__':
    
    # select the running mode:
    flag_mode=input("select mode : 0 for simulation results, 1: for running estimation")
    
    
        
    
    N=5
    rng_seed=123
    T=300
    T_end=60
    info_flag=0
    if flag_mode == "0" : 
        SIMU=Simu(rng_seed,Simu_para_dict)
        simu_data=SIMU.Data_simu(N,T,T_end,info_flag,flag_mode)
        
        
        pk.dump(simu_data, open( "simu_data.pkl", "wb"))
        
        
        
    else:
        simu_data = pk.load( open( "simu_data.pkl", "rb"))
    
    
        rng_seed=789
        SS=25
        JJ=6000
        info_flag=0
        print("fail")
        #est=Est(N,rng_seed,TT,SS,info_flag)
        
        d_struct={
                'N':N,
                'T':T,
                'rng_seed':rng_seed,
                'T_end':T_end,
                'SS':SS,
                "JJ":JJ,
                "info_flag": 0 ,
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
            







# ‘Nelder-Mead’ 
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