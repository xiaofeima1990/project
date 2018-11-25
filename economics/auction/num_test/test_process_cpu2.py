# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 18:17:44 2018

@author: mgxgl
cluster process testing 
process pool can not support nested multiprocessing


"""

import multiprocessing
import os
import time

#def worker():
#    name = multiprocessing.current_process().name
#    print(name+ ' Starting')
#    time.sleep(2)
#    print(name+ ' Exiting')
#
#def my_service():
#    name = multiprocessing.current_process().name
#    print(name, ' Starting')
#    time.sleep(3)
#    print(name, ' Exiting')
#    
    
list_jobs=[0,1]
data1 = [['a', '1'], ['b', '2'], ['c', '3'], ['d', '4'],['j','5'] ]
data2 = [['e', '5'], ['f', '4'], ['g', '3'], ['h', '2'],['i','1']]
data=[data1,data2]


def jobs(ID,data,pool_execut):
    print('this is job {}'.format(ID+1))
    pool_execut.map_async(mp_worker,data)


def mp_worker(data):
    inputs = data[0] 
    the_time =data[1]
    print(" Processs {}\tWaiting {} seconds" .format(inputs, the_time))
    print('process id:', os.getpid())
    time.sleep(int(the_time))
    print(" Process {}\tDONE".format(inputs))

def mp_handler(cpu_num):
    p = multiprocessing.Pool(cpu_num)
    cpu_num_level2=3
    pool_execut_v=[]
    print("OK1")
    for ele in range(0,2):
        pool_execut_v.append(multiprocessing.Pool(cpu_num_level2))
    
    p.map_async(jobs, zip(range(0,2),data,pool_execut_v))


    
    
if __name__ == '__main__':
    cpu_num=multiprocessing.cpu_count()
    print('# of available cpu is {}'.format(cpu_num))
    cpu_num_level1=2
    
          
    mp_handler(cpu_num_level1)