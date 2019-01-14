# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 17:12:27 2019

@author: xiaofeima
this is used for New Simulation Test



"""
import matplotlib.pyplot as plt
import pickle as pk
import os,sys
sys.path.append('/storage/work/g/gum27/system/pkg/')

PATH = os.path.dirname(os.path.realpath(__file__))
lib_path= os.path.dirname(PATH) + '/lib/'
# lib_path= PATH + '/lib/'
sys.path.append(lib_path)

data_path= os.path.dirname(PATH) + '/data/Simu/'
from Update_rule import Update_rule
from est import Est
from ENV import ENV
import numpy as np
import pandas as pd


if __name__ == '__main__':
    # read the data 
    PATH= 'E:/github/Project/economics/auction/num_test/simu'
    # without the informed bidder 
    with open( data_path + "simu_data_10-rand.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( data_path + "simu_data_11-rand.pkl", "rb") as f :
        simu_data_1=pk.load( f)
        
    
    # subsampling https://stackoverflow.com/questions/18713929/subsample-pandas-dataframe
    # df.sample
    # sample(self, n=None, frac=None, replace=False, weights=None, random_state=None, axis=None) method of pandas.core.frame.DataFrame instance
    # Returns a random sample of items from an axis of object.



    # clean the data 
    df_0=simu_data_0[0]
    
    temp_df=simu_data_0[1]
    temp_df=temp_df.reset_index()
    temp_df.rename(columns={'index':'ID'},inplace= True)
    
    
    df_0=df_0.merge(temp_df,on='ID',how='inner')
    
    
    df_1=simu_data_1[0]
    temp_df=simu_data_1[1]
    temp_df=temp_df.reset_index()
    temp_df.rename(columns={'index':'ID'},inplace= True)
    
    df_1=df_1.merge(temp_df,on='ID',how='inner')


    # get real number of bidder 8 
    df_0_c=df_0[df_0['num_i']==8]
    df_1_c=df_1[df_1['num_i']==8]








    # -------------------------------------------------------------
    # 1: used for calculating equilibrium bidding premium a la Dionne et al 2009
    # 1.1 all the prices 
    #     pi(i,k,j) = b^1(i,k,j) - b^0(i,k,j) 
    #     for angent i, simulated replication j and bidding round k 
    # 1.2 winnig bid
    #     pi(i=2,k=N-1,j|I=1,k=N,j) = b^1(i,k,j|I=1,k=N,j) - b^0(i=2,k=N-1,j) 
    # -------------------------------------------------------------






    # -------------------------------------------------------------
    # 2: used for generating the value distribution under informed and 
    #    uninformed case. 
    # 2.1 fixed # of bidders: winning bid, bid freqency, 
	# 2.2 use possion process to randomize # of bidders. 
	# -------------------------------------------------------------




    # -------------------------------------------------------------
    # 3: try to find way to decompose the channels for the learning effect, 
    #    private value, and competitive effect.
    # -------------------------------------------------------------
    
    
    # draw general graph for the simulation