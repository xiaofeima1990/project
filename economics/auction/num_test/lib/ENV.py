# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 12:34:00 2018

@author: xiaofeima
Numerical Test 

This script is about Environemnt Setup:
 - info structure
new:
 - ENV deals with the common value and nosiy part 
   the private part need to combine the rank order of bidders
modify the private part
where mu_ai = a_1*i  ; var_ai = a_2*i 
No--add rank order to 'info_struct' so that I change the structure of the xi, vi, MU and SIGMA2 a little bit. 
Different bidders have different xi, vi, MU and SIGMA2 
After discussing with professor, keep mu_a the same across all bidders 

----- 01-09-2019 -------
make private mu as 0 and let noisy mu random
make covi based on order not just identical for all i = 1  

"""

import numpy as np
import copy


para_dict={

        "comm_mu":1,
        "priv_mu":0, # fix
        'epsilon_mu': 0,
        "comm_var":0.5,
        "priv_var":0.3,
        "epsilon_var":0.4,
        }



class ENV:
    def __init__(self, N, dict_para=para_dict):
        self.comm_mu  = dict_para['comm_mu']
        self.priv_mu  = 0
        self.beta     =dict_para['beta']
        # self.noise_mu = dict_para['epsilon_mu']  # set epsilon mu always zero
        self.noise_mu = 0 
        self.comm_var =dict_para['comm_var']
        self.priv_var =dict_para['priv_var']
        self.noise_var=dict_para['epsilon_var']
        self.N=N
        # self.res=res
        self.info_st={}
        self.info_Id={}
        self.uninfo={}
        


    def info_struct(self,info_flag,ord_index=None,res=1):
        self.info_st['N']=self.N
        self.info_st["beta"] = self.beta
        self.info_st['comm_var'] =self.comm_var 
        self.info_st['priv_var'] =self.priv_var 
        self.info_st['epsilon_var'] =self.noise_var 
        self.info_st['comm_mu']  =self.comm_mu + self.beta*np.log(res)
        # self.info_st['beta']  =self.beta
        # xi_mu and xi_sigma2 this is a list for each possible i 
        self.info_st['xi_mu'] = self.comm_mu+self.priv_mu*ord_index + self.noise_mu*info_flag + self.beta*np.log(res)
        # self.info_st['xi_sigma2'] =  self.comm_var+self.priv_var*ord_index + self.noise_var*info_flag
        self.info_st['xi_sigma2'] =  self.comm_var+self.priv_var*np.ones(self.N) + self.noise_var*info_flag

        # vi_mu and vi_sigma2 
        self.info_st['vi_mu']    =  self.comm_mu+self.priv_mu*ord_index + self.beta*np.log(res)
        # self.info_st['vi_sigma2'] =  self.comm_var+self.priv_var*ord_index
        self.info_st['vi_sigma2'] =  self.comm_var+self.priv_var*np.ones(self.N)

        # rivals's xi
        self.info_st['xi_rival_mu']=[]
        self.info_st['vi_rival_mu']=[]
        self.info_st['xi_rival_sigma2']=[]
        self.info_st['vi_rival_sigma2']=[]
        self.info_st['MU']=[]
        self.info_st['SIGMA2']=[]
        self.info_st['cov_istar']=[] # covariance between vi and x 
        for i in range(self.N):
            temp_order=copy.deepcopy(ord_index)
            temp_order=np.delete(temp_order,i)

            temp_info_v=copy.deepcopy(info_flag)
            temp_info_v=np.delete(temp_info_v,i)
            # covariance vi and x 
            temp_oo = np.zeros(self.N)
            temp_oo[i] = 1 
            self.info_st['cov_istar'].append( self.comm_var * np.ones(self.N) + self.priv_var * temp_oo )


            # this rival means the rival's mu and variance, i.e. vj and xj, still we have to count for private and nosiy part  
            self.info_st['xi_rival_mu'].append( self.comm_mu + self.priv_mu*temp_order + self.noise_mu*temp_info_v + self.beta*np.log(res))
            self.info_st['vi_rival_mu'].append( self.comm_mu + self.priv_mu*temp_order + self.beta*np.log(res))

            # self.info_st['xi_rival_sigma2'].append( self.comm_var + self.priv_var*temp_order + self.noise_var*temp_info_v )
            # self.info_st['vi_rival_sigma2'].append( self.comm_var + self.priv_var*temp_order  )
            self.info_st['xi_rival_sigma2'].append( self.comm_var + self.priv_var*np.ones(self.N-1) + self.noise_var*temp_info_v )
            self.info_st['vi_rival_sigma2'].append( self.comm_var + self.priv_var*np.ones(self.N-1)  )

            new_order  = np.append(ord_index[i], temp_order)
            new_info_v = np.append(info_flag[i],temp_info_v)
            self.info_st['MU'].append( self.comm_mu + self.beta*np.log(res) +self.priv_mu*new_order + self.noise_mu*new_info_v  )
            # temp_sigma2=self.priv_var*new_order + self.noise_var*new_info_v
            temp_sigma2=self.priv_var*np.ones(self.N) + self.noise_var*new_info_v
            self.info_st['SIGMA2'].append( np.diag(temp_sigma2) + np.ones([self.N,self.N])*self.comm_var )

        # # add extra ascending order for the MU and SIGMA2 
        # temp_order=np.array(range(0,self.N))
        # self.info_st['MU'].append( self.comm_mu+self.priv_mu*temp_order + self.noise_mu*info_flag  )
        # temp_sigma2=self.priv_var*np.ones(self.N) + self.noise_var*info_flag
        # self.info_st['SIGMA2'].append( np.diag(temp_sigma2) + np.ones([self.N,self.N])*self.comm_var )
        ## remember that MU and SIGMA2 have extra item that is used for generating R.V.
        return Info_result(self.info_st)



    
    
class Info_result(object):
    def __init__(self,info_dict):
        '''
        
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
    
    # @property 
    # def x_info_sigma2(self):
    #     '''
    #     return v i simga squre
    #     '''
    #     return self.info_dict['x_info_sigma2']
        
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
    def vi_rival_mu(self):
        '''
        return  v i's  rival mu
        '''
        return self.info_dict['vi_rival_mu']
    
    @property 
    def vi_rival_sigma2(self):
        '''
        return  v i's  rival sigma square 
        '''
        return self.info_dict['vi_rival_sigma2']


    @property 
    def SIGMA2(self):
        '''
        return big SIGMA
        '''
        return self.info_dict['SIGMA2']

    @property 
    def MU(self):
        '''
        return MU for 
        '''
        return self.info_dict['MU']
    
    @property 
    def comm_var(self):
        '''
        return comm_var for 
        '''
        return self.info_dict['comm_var']

    @property 
    def priv_var(self):
        '''
        return priv_var for 
        '''
        return self.info_dict['priv_var']

    @property 
    def epsilon_var(self):
        '''
        return epsilon_var for 
        '''
        return self.info_dict['epsilon_var']

    @property 
    def comm_mu(self):
        '''
        return mu for 
        '''
        return self.info_dict['comm_mu']


    @property 
    def cov_istar(self):
        '''
        return cov_istar for 
        '''
        return self.info_dict['cov_istar']

    @property 
    def beta(self):
        '''
        return mu for 
        '''
        return self.info_dict['beta'] 

    