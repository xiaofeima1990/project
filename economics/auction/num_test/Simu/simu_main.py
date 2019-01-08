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
from simu import Simu
from Update_rule import Update_rule
from est import Est
from ENV import ENV
import numpy as np
import pandas as pd


if __name__ == '__main__':
    # read the data 

    # without the informed bidder 
    with open( data_path + "simu_data_10.pkl", "rb") as f :
        simu_data_0=pk.load( f)
    # with the informed bidder
    with open( data_path + "simu_data_11.pkl", "rb") as f :
        simu_data_1=pk.load( f)
        
    