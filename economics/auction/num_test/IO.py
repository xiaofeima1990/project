# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 22:37:38 2018

@author: mgxgl
input output 
"""

##save the file with binary format 

import numpy as np

firstColFlt =np.linspace(0,9,10)
secColFlt   =np.linspace(90,99,10)

print(firstColFlt,secColFlt)

np.savez('binaryNonCompressed.npz', firstColFlt, secColFlt)
npzFile = np.load('binaryNonCompressed.npz')
print(npzFile.files)
print(npzFile['arr_1']) 






## pickle 

import pickle as pk

pk.dump(firstColFlt, open( "firstCol.pkl", "wb"))
readInFirstCol = pk.load( open( "firstCol.pkl", "rb"))
print(readInFirstCol)
