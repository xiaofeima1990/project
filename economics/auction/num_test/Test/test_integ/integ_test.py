# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 16:12:15 2018

@author: xiaofeima
this script is used to find ways to incresse the speed of numerical integration
https://stackoverflow.com/questions/35215161/most-efficient-way-to-map-function-over-numpy-array

next task : function approximation

"""


import os,sys

sys.path.append('/storage/work/g/gum27/system/pkg/')

'''
install the package :
    eg. I am in the work directory and want to install on the pkg 
    pip install --target=system/pkg/ package_name

'''

PATH = os.path.dirname(os.path.realpath(__file__))

lib_path= os.path.dirname(PATH) + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Simu/'

import numpy as np
from Update_rule import Update_rule
from ENV import ENV 
from functools import partial
import time
import pandas as pd

para_dict={

        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }

def signal_DGP(para,rng,N,JJ=1000):


    
    MU       =para.MU
    SIGMA2   =para.SIGMA2

    x_signal=rng.multivariate_normal(MU.flatten(),SIGMA2,JJ)

#    [x_signal,w_x]=qe.quad.qnwnorm(JJ*np.ones(N),MU.flatten(),SIGMA2)
#    info_index=public_info[3]
    
    
    return x_signal


reserve=0.8
pub_mu=10
T_end=80
N = 5
rng_seed=123
Rng=np.random.RandomState(rng_seed)


Env       =ENV(N, para_dict)
info_para  =Env.Uninform()

n_Tend=int((T_end-5)/2)
price_v = np.linspace(reserve*pub_mu,pub_mu*1.1, n_Tend)
price_v=np.append(price_v,np.linspace(1.12*pub_mu,pub_mu*1.8, n_Tend))
price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,int(T_end-2*n_Tend)))


x_signal=signal_DGP(info_para,Rng,N,5000)
Update_bid=Update_rule(info_para)
ss_state=[5,4,3,2,1]
bid = max(ss_state)+1


fun_c = partial(Update_bid.real_bid,bid=bid,state=ss_state,price_v=price_v) 


#start=time.time()
#result=np.vectorize(fun_c)(x_signal[:,0])
#end=time.time()
#print("vectorize time use : {} seconds".format(end-start))
#
#
start=time.time()
x_v=x_signal[:,0]
result=np.fromiter([Update_bid.real_bid(xi,bid,ss_state,price_v)[0][0] for xi in x_v], x_v.dtype)
end=time.time()
print("fromiter time use : {} seconds".format(end-start))



start=time.time()
x_v=x_signal[:,0]
x_v=pd.Series(x_v)
result=x_v.apply(Update_bid.real_bid,args=(bid,ss_state,price_v))
end=time.time()
print("apply time use : {} seconds".format(end-start))



'''
compare with the simple function
'''

def f_test(x,para):
    return sum([x*ele for ele in para])


start=time.time()
x_v=x_signal[:,0]
result=np.fromiter([f_test(xi,ss_state) for xi in x_v], x_v.dtype)
end=time.time()
print("fromiter time use : {} seconds".format(end-start))



'''
function approximation
'''
