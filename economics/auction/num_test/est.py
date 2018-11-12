# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 00:39:34 2018

@author: mgxgl
this is for estimation 

"""

import numpy as np


para_dict={
        "comm_mu":10,
        "priv_mu":1,
        "noise_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "noise_var":0.8,
        }



class est:
    def __init__(self,N,rng_seed=789):
        self.N=N
        self.rng=np.random.RandomState(rng_seed)
        # set up the setup
        
    
    def para_setup(self,para_dict,SS=25):
        comm_mu =para_dict['comm_mu']
        priv_mu  = para_dict['priv_mu']
        epsilon_mu   = para_dict['epsilon_mu']
        
        comm_var = para_dict['comm_var']
        priv_var = para_dict['priv_var']
        epsilon_var = para_dict['epsilon_var']
        
        
        
        # setup new parameters 
        info['xi_mu']     =  self.comm_mu+self.priv_mu + self.noise_mu
        info['xi_sigma2'] =  self.comm_var+self.priv_var + self.noise_var
        info['vi_mu']     =  self.comm_mu+self.priv_mu 
        info['vi_sigma2'] =  self.comm_var+self.priv_var
        info['N']         =  self.N
        info['xi_rival_mu'] = (self.comm_mu+self.priv_mu + self.noise_mu) * np.ones((self.N-1,1))
        info['xi_rival_sigma2'] = (self.comm_var+self.priv_var + self.noise_var) * np.ones((self.N-1,1))
        info['vi_rival_mu'] = (self.comm_mu+self.priv_mu) * np.ones((self.N-1,1))
        info['vi_rival_sigma2'] = (self.comm_var+self.priv_var ) * np.ones((self.N-1,1))
        temp_matrix= np.ones((self.N,self.N))*self.comm_var - np.eye(self.N)*self.comm_var              
        info['COV_i']       = np.concatenate((np.diag(info['vi_sigma2']*np.ones(self.N)) + temp_matrix ), axis=1)
        info['SiGMA2']      = info['xi_sigma2']*np.ones((self.N,self.N)) + temp_matrix
        info['MU']          = (self.comm_mu+self.priv_mu + self.noise_mu)*np.ones((self.N,1))
        info['comm_var']    = self.comm_var
        info['comm_mu']    = self.comm_mu
        info['SS']         = SS
        return Info_result(info)
    
    
    def signal_DGP_est(self,public_info,Theta):
        
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
        
        x_signal=self.rng.normal(mu_x,sigma_x,self.N)
        
        info_index=public_info[3]
        
        if info_index >0:
            mu_x = self.comm_mu+self.priv_mu
            sigma_x = self.comm_var + self.priv_var
        
            x_info=self.rng.normal(mu_x,sigma_x)
            
            x_signal[info_index]=x_info
        
        
        
        return [pub_mu,x_signal,r,info_index]
    
    def SMM(self,Data_struct,Theta):
        
        para=para_setup(Theta)
        SS=para.SS
        TT=para.TT
        
        Update_rule=Update_bid(para)
        Sg=np.zeros(10)
        
        for tt in range(0,TT):
        
            data_act=np.zeros((SS,T_end))
            
            data_state=np.zeros((SS,self.N))
            data_bid_freq=np.zeros((SS,self.N))
            data_win=np.zeros((SS,1))
            
            freq_i=np.zeros((SS,1))
            num_i = np.zeros((SS,1))
            diff_i = np.zeros((SS,1))
            win_low=np.zeros((SS,1))
            win_up =np.zeros((SS,1))
            # Active_flag=np.ones(self.N)
            flag_ID=0
            for s in range(0,SS):
                [pub_mu,x_signal, reserve,info_index]=self.signal_DGP_est(Data_struct.public_info,Theta)
                
                
                price_v=[np.linspace(0.8*pub_mu,pub_mu*1.2, 30),np.linspace(1.24*pub_mu,pub_mu*1.8, 5),np.linspace(1.85*pub_mu,pub_mu*2.5,5)];
            
                State = np.zeros(self.N)
                Active= np.ones(self.N)
                
                
                for t in range(0,T_end):
                    
                    if t == 1: 
                        curr_bidder=np.argmax(x_signal)
                        data_act[s,t] = curr_bidder
                        State[curr_bidder]=State[curr_bidder]+1
                    else:
                        
                        for i in range(0,self.N):
                            temp_state=State
                            
                            ii = temp_state[i]
                            temp_state=np.delete(temp_state,i)
                            i1 = temp_state[0]
                            i2 = temp_state[1]
                            ss_state = [ii,i1,i2]
                   
                            bid = max(ss_state)+1
                            result = Update_rule.real_bid(x_signal(i),bid,ss_state,price_v)
                            
                            Active[i] = result[2]
                            
                            
                        if sum(Active) ==1:
                            index=np.nonzero(Active)
                            posting=data_act[s,t-1]
                            if index == posting:
                                data_act[s,t:] = -1
                            else:
                                curr_bidder      = index
                                data_act[s,t]    = curr_bidder
                                data_act[s,t+1:] = -1
                            
                            break
                        else :
                            if sum(Active) == 0:
                                data_act[s,t:] = -1
                                break
                            
                            
                            
                            posting=data_act[s,t-1]
                            index=np.nonzero(Active)
                            if posting in index :
                                index.reomve(posting)
                               
                           
                           
                            curr_bidder   = rng.choice(index,size=1) 
                            data_act[s,t] = curr_bidder
                            State[curr_bidder] = max(State) + 1
               
            
                # final state
                data_state[s,:]=State
                
                # calculate the high posit
                unique, counts = np.unique(data_act[s,:], return_counts=True)
                a=zip(unique,counts) 
                for ele in a:
                    if ele[0] != -1:
                        data_bid_freq[s,ele[0]]=ele[1]
                    else:
                        continue
                        
                # comb = list(combinations(list(range(0,self.N)), 2))
                comb=np.array(np.meshgrid(data_bid_freq[s,:], data_bid_freq[s,:])).T.reshape(-1,2)
                v=abs(comb[:,0]-comb[:,1])
                freq_i(s)=sum(v)
    
                
                
                # winning
                data_win[s]=para.T_p(max(State)) / (pub_mu*reserve)
                
                # high posit
                diff_i[s]=std(max(State)-State)
                
                
                # find real bidding bidders
                num_i[s]  =sum((State>0)*1)
                
                temp_state=State
                            
                i = np.argmax(temp_state)
                ii=  max(temp_state)
                temp_state=np.delete(temp_state,i)
                i1 = temp_state[0]
                i2 = temp_state[1]
                ss_state = [ii,i1,i2]
       
                bid = ii
                result = Update_rule.real_bid(x_signal(i),bid,ss_state,price_v)
                win_low[s]=result[0]
                
                bid = bid = ii+1
                result = Update_rule.real_bid(x_signal(i),bid,ss_state,price_v)
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
            Sg[2]=Sg[2]+Data_struct.diff_i[tt]   - SM["num_i_mu"]
            Sg[3]=Sg[3]+Data_struct.num_i[tt]    - SM["diff_i_mu"]
            Sg[4]=Sg[4]+Data_struct.Data_win2[tt]- SM["data_win_var"]
            Sg[5]=Sg[5]+Data_struct.freq_i[tt]   - SM["freq_i_var"]
            Sg[6]=Sg[6]+Data_struct.diff_i[tt]   - SM["num_i_var"]
            Sg[7]=Sg[7]+Data_struct.num_i[tt]    - SM["diff_i_var"]
            Sg[8]=Sg[8]+Data_struct.data_win[tt] - SM["win_low"]
            Sg[9]=Sg[9]+Data_struct.data_win[tt] - SM["win_up"]

        
        Sg=Sg/TT
        

        return sum(np.square(Sg))
        
        

    
    
    
class Info_result(object):
    def __init__(self,info_dict):
        '''
        mesure the distance include
        1. miles
        2. kilometers
        3. meters
        4. feet
        distance_measure={
          'miles':, 
          'kilometers':,
          'meters':,
          'feet',
        
        }
        
        '''
        self.info_dict=info_dict
    @property 
    def xi_mu(self):
        '''
        return x i mu
        '''
        return self.info_dict['xi_mu']

    @property 
    def xi_sigma2(self):
        '''
        return x i sigma square
        '''
        return self.info_dict['xi_sigma2']     
    @property 
    def vi_mu(self):
        '''
        return x i mu
        '''
        return self.info_dict['vi_mu']
    @property 
    def vi_sigma2(self):
        '''
        return v i simga squre
        '''
        return self.info_dict['vi_sigma2']
    
    @property 
    def x_info_mu(self):
        '''
        return x i mu
        '''
        return self.info_dict['x_info_mu']
    
    @property 
    def x_info_sigma2(self):
        '''
        return v i simga squre
        '''
        return self.info_dict['x_info_sigma2']
        
    @property 
    def N(self):
        '''
        return number of bidder
        '''
        return self.info_dict['N']

    @property 
    def xi_rival_mu(self):
        '''
        return x i's  rival mu 
        '''
        return self.info_dict['xi_rival_mu']

    @property 
    def xi_rival_sigma2(self):
        '''
        return  x i's  rival sigma square 
        '''
        return self.info_dict['xi_rival_sigma2']

    @property 
    def COV_i(self):
        '''
        return Sigma i 
        '''
        return self.info_dict['COV_i']

    @property 
    def SiGMA2(self):
        '''
        return big SIGMA
        '''
        return self.info_dict['SiGMA2']

    @property 
    def MU(self):
        '''
        return mu for 
        '''
        return self.info_dict['MU']
    
    @property 
    def comm_var(self):
        '''
        return mu for 
        '''
        return self.info_dict['comm_var']

    @property 
    def comm_mu(self):
        '''
        return mu for 
        '''
        return self.info_dict['comm_mu']
    
    
    @property 
    def SS(self):
        '''
        return mu for 
        '''
        return self.info_dict['SS']
    
    
        
