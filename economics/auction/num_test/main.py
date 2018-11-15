# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 15:49:59 2018

@author: xiaofeima
This is main program to run the estimation

1generate simualation result
2doing estimation

doing paramellal programming

"""
import numpy as np
from simu import Simu
from Update_rule import Update_rule
from est import Est
from ENV import ENV
from scipy.optimize import minimize
import copy ,time
from collections import defaultdict,OrderedDict
from scipy.stats import multivariate_normal


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
   



def signal_DGP_est(public_info,Theta,rng,N):
    
    comm_mu =Theta['comm_mu']
    priv_mu  = Theta['priv_mu']
    epsilon_mu   = Theta['epsilon_mu']
    
    comm_var = Theta['comm_var']
    priv_var = Theta['priv_var']
    epsilon_var = Theta['epsilon_var']
    
    # common value in public
    pub_mu = public_info[0]
    
    # random reservation ratio
    # r =  0.8 + 0.1*self.rng.rand() 
    r =  public_info[2]
    
    
    mu_x = comm_mu+priv_mu+epsilon_mu
    sigma_x = comm_var + priv_var+ epsilon_var
    
    x_signal=rng.normal(mu_x,sigma_x,N)
    
    info_index=public_info[3]
    
    if info_index >0:
        mu_x     = comm_mu+ priv_mu
        sigma_x  = comm_var + priv_var
    
        x_info   = rng.normal(mu_x,sigma_x)
        
        x_signal[info_index]=x_info
    
    
    
    return [pub_mu,x_signal,r,info_index]

def signal_DGP_simu(public_info,para,rng,N,JJ=100):
    

    
    MU       =para.MU
    SIGMA2   =para.SIGMA2
    # common value in public
    pub_mu = public_info[:,0]
    
    # random reservation ratio
    # r =  0.8 + 0.1*self.rng.rand() 
    r =  public_info[:,1]
    
    
    print(MU)
    x_signal=rng.multivariate_normal(MU.flatten(),SIGMA2,JJ)
    
    info_index=public_info[3]
    
    prob_x_signal=multivariate_normal.pdf(x_signal,MU.flatten(),SIGMA2)
    
    
    
    return [pub_mu,x_signal,prob_x_signal,info_index,r]



def SMM(Theta0,Data_struct,d_struct):
    
    Theta={
    "comm_mu":Theta0[0],
    "priv_mu":Theta0[1],
    "epsilon_mu":Theta0[2],
    "comm_var":Theta0[3],
    "priv_var":Theta0[4],
    "epsilon_var":Theta0[5],
    }

    N=d_struct['N']
    T_end=d_struct['T_end']
    SS=d_struct['SS']
    TT=d_struct['T']
    
    # setup the env info structure
    Env=ENV(N, Theta)
    if info_flag == 0 :
        para=Env.Uninform()
    else:
        para=Env.Info_ID()
    
    rng=np.random.RandomState(d_struct['rng_seed'])
    Update_bid=Update_rule(para)
    Sg=np.zeros(10)
    start = time.time()
    print('--------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
    print('# of auctions: '+str(TT) + '\t # of simus: '+str(SS))
    
    for tt in range(0,TT):
    
        data_act=np.zeros((SS,T_end))
        
        data_state=np.zeros((SS,N))
        data_bid_freq=np.zeros((SS,N))
        data_win=np.zeros((SS,1))
        
        freq_i=np.zeros((SS,1))
        num_i = np.zeros((SS,1))
        diff_i = np.zeros((SS,1))
        win_low=np.zeros((SS,1))
        win_up =np.zeros((SS,1))
        # Active_flag=np.ones(N)

        for s in range(0,SS):
            [pub_mu,x_signal, reserve,info_index]=signal_DGP_est(Data_struct.pub_info[s,:],Theta,rng,N)
            
            
            price_v = np.linspace(0.8*pub_mu,pub_mu*1.2, T_end-10)
            price_v=np.append(price_v,np.linspace(1.24*pub_mu,pub_mu*1.8, 5))
            price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,5))
            
            State = np.zeros(N)
            Active= np.ones(N)
            
            
            for t in range(0,T_end):
                
                if t == 0: 
                    curr_bidder=int(np.argmax(x_signal))
                    data_act[s,t] = curr_bidder
                    State[curr_bidder]=State[curr_bidder]+1
                else:
                    
                    for i in range(0,N):
                        temp_state=State
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)
                        i1 = int(temp_state[0])
                        i2 = int(temp_state[1])
                        ss_state = [ii,i1,i2]
               
                        bid = max(ss_state)+1
                        result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
                        
                        Active[i] = result[2]
                        
                        
                    if sum(Active) ==1:
                        index=np.nonzero(Active)[0].tolist()
                        
                        posting=data_act[s,t-1]
                        if index == posting:
                            data_act[s,t:] = int(-1)
                        else:
                            curr_bidder      = int(index[0])
                            data_act[s,t]    = int(curr_bidder)
                            State[int(curr_bidder)] = max(State) + 1
                            data_act[s,t+1:] = int(-1)
                        
                        break
                    else :
                        if sum(Active) == 0:
                            data_act[s,t:] = int(-1)
                            break
                        
                        
                        
                        posting=data_act[s,t-1]
                        index=np.nonzero(Active)[0].tolist()
                        if posting in index :
                            index.remove(posting)
                           
                       
                       
                        curr_bidder   = rng.choice(index,size=1) 
                        data_act[s,t] = int(curr_bidder)
                        State[curr_bidder] = max(State) + 1
           
        
            # final state
            data_state[s,:]=State
            
            # calculate the high posit
            unique, counts = np.unique(data_act[s,:], return_counts=True)
            a=zip(unique,counts) 
            for ele in a:
                if ele[0] != -1:
                    data_bid_freq[s,int(ele[0])]=ele[1]
                else:
                    continue
                    
            # comb = list(combinations(list(range(0,self.N)), 2))
            comb=np.array(np.meshgrid(data_bid_freq[s,:], data_bid_freq[s,:])).T.reshape(-1,2)
            v=abs(comb[:,0]-comb[:,1])
            freq_i[s]=sum(v)

            
            
            # winning
            data_win[s]=price_v[int(max(State))] / (pub_mu*reserve)
            
            # high posit
            diff_i[s]=np.std(max(State)-State)
            
            
            # find real bidding bidders
            num_i[s]  =int(sum((State>0)*1))
            
            temp_state=State
                        
            i = np.argmax(temp_state)
            ii=  int(max(temp_state))
            temp_state=np.delete(temp_state,i)
            i1 = int(temp_state[0])
            i2 = int(temp_state[1])
            ss_state = [ii,i1,i2]
   
            bid = ii
            result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
            win_low[s]=result[0]
            
            bid =  ii+1
            result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
            win_up[s]=result[0]                
            
        
        SM={
            "data_win_mu":np.mean(data_win),
            "freq_i_mu":np.mean(freq_i),
            "num_i_mu":np.mean(num_i),
            "diff_i_mu":np.mean(diff_i),
            "data_win_var":np.var(data_win),
            "freq_i_var":np.var(freq_i),
            "num_i_var":np.var(num_i),
            "diff_i_var":np.var(diff_i),   
            "win_low": np.mean(win_low),
            "win_up": np.mean(win_up),
            }
    
    # calcuate the winning value 

        
        
        Sg[0]=Sg[0]+Data_struct.data_win[tt] - SM["data_win_mu"]
        Sg[1]=Sg[1]+Data_struct.freq_i[tt]   - SM["freq_i_mu"]
        Sg[2]=Sg[2]+Data_struct.diff_i[tt]   - SM["diff_i_mu"]
        Sg[3]=Sg[3]+Data_struct.num_i[tt]    - SM["num_i_mu"]
        Sg[4]=Sg[4]+Data_struct.data_win2[tt]- SM["data_win_var"]
        Sg[5]=Sg[5]+Data_struct.freq_i2[tt]   - SM["freq_i_var"]
        Sg[6]=Sg[6]+Data_struct.diff_i2[tt]   - SM["diff_i_var"]
        Sg[7]=Sg[7]+Data_struct.num_i2[tt]    - SM["num_i_var"]
        Sg[8]=Sg[8]+Data_struct.data_win[tt] - SM["win_low"]
        Sg[9]=Sg[9]+Data_struct.data_win[tt] - SM["win_up"]

    
    Sg=Sg/TT
    
    end = time.time()
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')

    return sum(np.square(Sg))

def GMM_Ineq(Theta0,Data_struct,d_struct):
    Theta={
    "comm_mu":Theta0[0],
    "priv_mu":Theta0[1],
    "epsilon_mu":Theta0[2],
    "comm_var":Theta0[3],
    "priv_var":Theta0[4],
    "epsilon_var":Theta0[5],
    }

    N     =d_struct['N'] # number of bidders for the highest bidding price
    T_end =d_struct['T_end']
    J     =d_struct["JJ"]
    
    TT=d_struct['T'] # number of auctions in the data
    
    # setup the env info structure
    Env=ENV(N, Theta)
    if info_flag == 0 :
        para=Env.Uninform()
    else:
        para=Env.Info_ID()
    
    rng=np.random.RandomState(d_struct['rng_seed'])
    Update_bid=Update_rule(para)

    start = time.time()
    
    MoM=0
    
    [pub_mu,x_signal,prob_x_signal,info_index,resev]=signal_DGP_simu(Data_struct.pub_info,para,rng,N,J)
    
    print('--------------------------------------------------------')
    print('current parameter set are :')
    print(Theta)
    print('# of auctions: '+str(TT) + '\t # of simus: '+str(SS))
    
    for tt in range(0,TT):
        temp_act= copy.deepcopy(Data_struct.data_act[tt,:])
        temp_state=copy.deepcopy(Data_struct.data_state[tt,:])
        
        can_bidder_lists=list(list_duplicates(temp_act))
        can_bidder_lists=[x for x in can_bidder_lists if x[0] != -1 ]
        can_bidder_lists.sort()
        
        state_temp=np.zeros((N,N))
        pub_mu_0=pub_mu[tt]
        
        price_v = np.linspace(resev[tt]*pub_mu_0,pub_mu_0*1.2, T_end-10)
        price_v=np.append(price_v,np.linspace(1.24*pub_mu_0,pub_mu_0*1.8, 5))
        price_v=np.append(price_v,np.linspace(1.85*pub_mu_0,pub_mu_0*2.5,5))
            
        # get the bidders state for claculation
        for i in range(0,len(temp_state)):
            flag_select=[1,1,1]
            flag_select[i]=0
            select_flag=np.nonzero(flag_select)[0].tolist()
            i_list=[0]
            i_list=i_list + can_bidder_lists[i][1]
            state_temp[i,0]=[x for x in can_bidder_lists[i][1]][-2]
            
            temp_s=[]
            for j in select_flag:
                bid_post=can_bidder_lists[j][1]
                bid_post.append(0)
                temp_s.append([x for x in bid_post[i][1] if x < temp_state[i] ][-2])
            
            state_temp[i,1:] = temp_s
            
            
        # for the expected value of each bidders
        

        bid_low=[price_v(x) for x in temp_state]
        bid_up =price_v(int(max(temp_state)+1))*np.ones(3)
        
        
        
        
        
        # now I need to calculate empirical int 
        for j in range(0,J):
            
            exp_value=np.zeros(3)
            low_case =np.zeros(3)
            up_case  =np.zeros(3)
            
            
            for i in range(0,N):
                bid=int(max(state_temp[i,:]))+1
                result = Update_bid.real_bid(x_signal[j,i],bid,state_temp,price_v)
                
                exp_value[i]=result[0]
            
            # calcuate the first part b-exp<= 0 
            low_case=bid_low-exp_value
            up_case =bid_up-exp_value
        
            
            exp_value=sum(np.square((low_case>0)*1*low_case)) + sum(np.square((up_case<0)*1*up_case))
            
            exp_value=exp_value*prob_x_signal[j] + exp_value
                
                
                
            
            
        MoM = MoM + exp_value
            
    end = time.time()
    print("time spend in this loop: ")
    print(end - start)
    print('--------------------------------------------------------\n')
 
    return MoM


if __name__ == '__main__':
    
    # fminsearch
    N=3
    rng_seed=123
    T=50
    T_end=40
#    SIMU=Simu(N,T,rng_seed,Simu_para_dict)
#    simu_data=SIMU.Data_simu(T_end)
##    
    
    
    rng_seed=789
    SS=25
    JJ=100
    info_flag=0
    
    #est=Est(N,rng_seed,TT,SS,info_flag)
    
    d_struct={
            'N':N,
            'T':T,
            'rng_seed':rng_seed,
            'T_end':T_end,
            'SS':SS,
            "JJ":JJ,
            
            }
    
#    Theta= copy.deepcopy(Simu_para_dict)
    
    Theta=[10,1,0,0.8,1.2,0.8]
#    s=SMM(Theta,simu_data,d_struct)
    s=GMM_Ineq(Theta,simu_data,d_struct)
    # start the estimation 
#    res = minimize(SMM, Theta, method='nelder-mead',args=(simu_data,simu_data,d_struct))