# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 12:06:39 2018

@author: mgxgl
test for nested parallel programming
"""

#from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
#import time
#from functools import partial
#pool = ThreadPoolExecutor(max_workers=3)
#
#def find_work_inputs(dummy_file):
#    print("{}: Finding work...".format(dummy_file))
#    time.sleep(1)
#    work = range(0, dummy_file)
#    print("{}: Work is {}".format(dummy_file, work))
#    return work
#
#def do_work(dummy_file, work_input):
#    print("{}: {}".format(dummy_file, work_input))
#    print("{}: Doing work {}...".format(dummy_file, work_input))
#    time.sleep(1)
#    return work_input * work_input
#
#dummy_files = [1,2,3,4,5]
#
#futures = []
#for dummy_file in dummy_files:
#    work_inputs = pool.submit(find_work_inputs, dummy_file)
#    for work_input in work_inputs.result():
#        result = work_input
#        futures.append((dummy_file, result, pool.submit(do_work, dummy_file, result)))
#
#for dummy_file, work_input, future in futures:
#    print("Result from file:{} input:{} is {}".format(dummy_file, work_input, future.result()))
#    
    
'''
test for process
'''
#
#pool = ProcessPoolExecutor(max_workers=3)
#
#def find_work_inputs(dummy_file):
#    print("{}: Finding work...".format(dummy_file))
#    time.sleep(1)
##    work = range(0, dummy_file)
#    work = dummy_file
#    print("{}: Work is {}".format(dummy_file, work))
#    return work
#
#def do_work(dummy_file, work_input):
#    print("{}: {}".format(dummy_file, work_input))
#    print("{}: Doing work {}...".format(dummy_file, work_input))
#    time.sleep(1)
#    return work_input * work_input
#
#
#
#
#if __name__ == '__main__':
#
#    dummy_files = [1,2,3,4,5]
#    
#    futures = []
#
#    for dummy_file in dummy_files:
#        work_inputs=pool.submit(find_work_inputs, dummy_file)
#        
##        for work_input in work_inputs.result():
##            result = work_input
#        result=work_inputs.result()
#        print('current working dummy {} and result {}'.format(dummy_file,result))
##        print("the first level result is {}".format(result))
#        futures.append((dummy_file, result, pool.map(partial(do_work, dummy_file), range(0,result))))
#
#    for dummy_file, work_input, future in futures:
#        print("Result from file:{} input:{} is {}".format(dummy_file, work_input, [x for x in future]))
#        
#

'''
-------------------------------------------------------------------------------
real nested parallel 

 each thread on the first level needs to trigger the work themselves.

'''
#from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
#import time
#from functools import partial
#import threading
#
#
#def find_work_inputs(dummy_file,do_work_pool):
#    print("{}: Finding work...".format(dummy_file))
#    time.sleep(2)
#    work = range(0, dummy_file)
#    print("{}: Work is {}".format(dummy_file, work))
#    print('level 1 thread ID is {}'.format(threading.get_ident()))
#    futures = []
#    for work_input in work:
#        futures.append((dummy_file, work_input, do_work_pool.submit(do_work, dummy_file, work_input)))
#    return futures
#
#def do_work(dummy_file, work_input):
#    print("{}: {}".format(dummy_file, work_input))
#    print("{}: Doing work {}...".format(dummy_file, work_input))
#    print('level 2 thread ID is {}'.format(threading.get_ident()))
#    time.sleep(1)
#    
#    return work_input * work_input
#
#
#if __name__ == '__main__':
#    find_work_pool = ThreadPoolExecutor(max_workers=3)
#    do_work_pool=[]
#    for ele in range(0,6):
#        do_work_pool.append(ThreadPoolExecutor(max_workers=2))
#
#    dummy_files = [1,2,3,4,5,6]
#    
#    futures = []
#    for dummy_file in dummy_files:
#        futures.extend(find_work_pool.submit(find_work_inputs, dummy_file,do_work_pool[dummy_file]).result())
#    
#    for dummy_file, work_input, future in futures:
#        print("Result from file:{} input:{} is {}".format(dummy_file, work_input, future.result()))
#        

'''
process
'''
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import concurrent.futures
import time
from functools import partial
import threading
import os


def find_work_inputs(dummy_file):
    print("{}: Finding work...".format(dummy_file))
    time.sleep(1)
    work = range(0, dummy_file)
    print("{}: Work is {}".format(dummy_file, work))
    print('level 1 thread ID is {}'.format(threading.get_ident()))
    futures = []
    do_work_pool=ProcessPoolExecutor(max_workers=2)
        
    futures.append((dummy_file, work, do_work_pool.map(partial(do_work, dummy_file), work)))
    
    return futures

def do_work(dummy_file, work_input):
    print("{}: {}".format(dummy_file, work_input))
    print("{}: Doing work {}...".format(dummy_file, work_input))
    print('process id:', os.getpid())   
    time.sleep(1)
    
    return work_input * work_input


if __name__ == '__main__':
    find_work_pool = ThreadPoolExecutor(max_workers=3)
#    do_work_pool=[]
#    for ele in range(0,3):
#        do_work_pool.append(ProcessPoolExecutor(max_workers=2))

    dummy_files = [1,2,3]
    
    futures = []
    for dummy_file in dummy_files:
        futures.extend(find_work_pool.submit(find_work_inputs, dummy_file).result())
    
#    concurrent.futures.wait(futures)
    
    for dummy_file, work_input, future in futures:
        print("Result from file:{} input:{} is {}".format(dummy_file, work_input, sum(future)))