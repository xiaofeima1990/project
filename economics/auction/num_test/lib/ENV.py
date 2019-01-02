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

"""

import numpy as np
import copy


para_dict={

        "comm_mu":1,
        "priv_mu":0,
        "beta":1,
        "comm_var":0.5,
        "priv_var":0.3,
        "epsilon_var":0.4,
        }



class ENV:
    def __init__(self, N, dict_para=para_dict,ord_index=None,info_flag=np.zeros(3)):
        self.comm_mu  =dict_para['comm_mu']
        self.priv_mu  =dict_para['priv_mu']
        self.beta     =dict_para['beta']
        self.noise_mu = 0  # set epsilon mu always zero
        self.comm_var =dict_para['comm_var']
        self.priv_var =dict_para['priv_var']
        self.noise_var=dict_para['epsilon_var']
        self.N=N
        self.order=ord_index
        self.info_flag=info_flag
        self.info_st={}
        self.info_Id={}
        self.uninfo={}
        


    def info_struct(self):
        self.info_st['N']=self.N
        self.info_st['comm_var'] =self.comm_var 
        self.info_st['comm_mu']  =self.comm_mu
        self.info_st['beta']  =self.beta
        # xi_mu and xi_sigma2 this is a list for each possible i 
        self.info_st['xi_mu'] = self.comm_mu+self.priv_mu*self.order + self.noise_mu*self.info_flag
        self.info_st['xi_sigma2'] =  self.comm_var+self.priv_var*self.order + self.noise_var*self.info_flag

        # vi_mu and vi_sigma2 
        self.info_st['vi_mu']    =  self.comm_mu+self.priv_mu*self.order 
        self.info_st['vi_sigma2'] =  self.comm_var+self.priv_var*self.order

        # rivals's xi
        self.info_st['xi_rival_mu']=[]
        self.info_st['vi_rival_mu']=[]
        self.info_st['xi_rival_sigma2']=[]
        self.info_st['vi_rival_sigma2']=[]
        self.info_st['MU']=[]
        self.info_st['SIGMA2']=[]
        for i in range(len(self.order)):
            temp_order=copy.deepcopy(self.order)
            temp_order=np.delete(temp_order,i)

            temp_info_v=copy.deepcopy(self.info_flag)
            temp_info_v=np.delete(temp_info_v,i)

            self.info_st['xi_rival_mu'].append( self.comm_mu + self.priv_mu*temp_order+ self.noise_mu*temp_info_v )
            self.info_st['vi_rival_mu'].append( self.comm_mu + self.priv_mu*temp_order )

            self.info_st['xi_rival_sigma2'].append( self.comm_var + self.priv_var*temp_order + self.noise_var*temp_info_v )
            self.info_st['vi_rival_sigma2'].append( self.comm_var + self.priv_var*temp_order  )

            new_order  = np.append(self.order[i], temp_order)
            new_info_v = np.append(self.info_flag[i],temp_info_v)
            self.info_st['MU'].append( self.comm_mu+self.priv_mu*new_order + self.noise_mu*new_info_v )
            temp_sigma2=self.priv_var*new_order + self.noise_var*new_info_v
            self.info_st['SIGMA2'].append( np.diag(temp_sigma2) + np.ones([self.N,self.N]) )
            
        return Info_result(self.info_st)




    def Uninform(self):
        
        
        
        self.uninfo['xi_mu']     =  self.comm_mu+self.priv_mu + self.noise_mu
        self.uninfo['xi_sigma2'] =  self.comm_var+self.priv_var + self.noise_var
        self.uninfo['vi_mu']     =  self.comm_mu+self.priv_mu 
        self.uninfo['vi_sigma2'] =  self.comm_var+self.priv_var
        
        self.uninfo['xi_rival_mu'] = (self.comm_mu+self.priv_mu + self.noise_mu) * np.ones((self.N-1,1))
        self.uninfo['xi_rival_sigma2'] = (self.comm_var+self.priv_var + self.noise_var) * np.ones((self.N-1,1))
        self.uninfo['vi_rival_mu'] = (self.comm_mu+self.priv_mu) * np.ones((self.N-1,1))
        self.uninfo['vi_rival_sigma2'] = (self.comm_var+self.priv_var ) * np.ones((self.N-1,1))
        temp_matrix= np.ones((self.N,self.N))*self.comm_var - np.eye(self.N)*self.comm_var               
        self.uninfo['SIGMA2']      = np.diag(self.uninfo['xi_sigma2']*np.ones(self.N)) + temp_matrix
        self.uninfo['MU']          = (self.comm_mu+self.priv_mu + self.noise_mu)*np.ones((self.N,1))

        self.uninfo['comm_var']    = self.comm_var
        self.uninfo['comm_mu']    = self.comm_mu
        self.uninfo['N']         =  self.N

        self.uninfo['beta']=self.beta
        return Info_result(self.uninfo)
        
    def Info_ID(self):
        self.info_Id['xi_mu']     =  self.comm_mu+self.priv_mu + self.noise_mu
        self.info_Id['xi_sigma2'] =  self.comm_var+self.priv_var + self.noise_var
        self.info_Id['vi_mu']     =  self.comm_mu+self.priv_mu
        self.info_Id['vi_sigma2'] =  self.comm_var+self.priv_var
        self.info_Id['x_info_mu'] = self.comm_mu+self.priv_mu 
        
        self.info_Id['x_info_sigma2'] = self.comm_var+self.priv_var
        self.info_Id['N']         =  self.N
        temp_N2=(self.comm_mu+self.priv_mu + self.noise_mu) * np.ones((self.N-2,1))
        self.info_Id['xi_rival_mu'] = np.concatenate(((self.comm_mu+self.priv_mu)*np.ones((1,1)) , temp_N2), axis=0)
        self.info_Id['vi_rival_mu'] = np.concatenate(((self.comm_mu+self.priv_mu)*np.ones((1,1)) , temp_N2), axis=0)
        temp_N2=(self.comm_var+self.priv_var + self.noise_var) * np.ones((self.N-2,1))
        self.info_Id['xi_rival_sigma2'] = np.concatenate(((self.comm_var+self.priv_var)*np.ones((1,1)) , temp_N2), axis=0)
        self.info_Id['vi_rival_sigma2'] = (self.comm_var+self.priv_var ) * np.ones((self.N-1,1))
        temp_matrix= np.ones((self.N,self.N))*self.comm_var - np.eye(self.N)*self.comm_var              
        self.info_Id['COV_i']       = np.diag(self.info_Id['vi_sigma2']*np.ones(self.N)) + temp_matrix 
        temp_var=self.info_Id['xi_sigma2']*np.ones(self.N)
        temp_var[1]=self.info_Id['x_info_sigma2']
        self.info_Id['SIGMA2']      = np.diag(temp_var) + temp_matrix
        self.info_Id['MU']          = (self.comm_mu+self.priv_mu + self.noise_mu)*np.ones((self.N,1))
        
        self.info_Id['comm_var']    = self.comm_var
        self.info_Id['comm_mu']    = self.comm_mu
        
        self.info_Id['MU'][1,0]=self.info_Id['x_info_mu']
        self.info_Id['xi_rival_mu'][0,0]=self.info_Id['x_info_mu']
        self.info_Id['vi_rival_mu'][0,0]=self.info_Id['x_info_mu']
        self.info_Id['beta']=self.beta
        return Info_result(self.info_Id)
    
    
    
    
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
    def beta(self):
        '''
        return mu for 
        '''
        return self.info_dict['beta'] 

    