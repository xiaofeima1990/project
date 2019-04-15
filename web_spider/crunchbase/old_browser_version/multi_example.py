# -*- coding: utf-8 -*-
"""
Created on Sun Jul  8 22:21:42 2018

@author: xiaofeima
"""

import multiprocessing as mp
import time

def foo_pool(x):
    time.sleep(2)
    return x*x

result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)

def apply_async_with_callback():
    pool = mp.Pool(2)
    for i in range(10):
        pool.apply_async(foo_pool, args = (i, ), callback = log_result)
    pool.close()
    pool.join()
    print(result_list)

if __name__ == '__main__':
    apply_async_with_callback()
    
    
'''    
Back in the old days of Python, to call a function with arbitrary arguments, you would use apply:

apply(f,args,kwargs)
apply still exists in Python2.7 though not in Python3, and is generally not used anymore. Nowadays,

f(*args,**kwargs)
is preferred. The multiprocessing.Pool modules tries to provide a similar interface.

Pool.apply is like Python apply, except that the function call is performed in a separate process. Pool.apply blocks until the function is completed.

Pool.apply_async is also like Python's built-in apply, except that the call returns immediately instead of waiting for the result. An ApplyResult object is returned. You call its get() method to retrieve the result of the function call. The get() method blocks until the function is completed. Thus, pool.apply(func, args, kwargs) is equivalent to pool.apply_async(func, args, kwargs).get().

In contrast to Pool.apply, the Pool.apply_async method also has a callback which, if supplied, is called when the function is complete. This can be used instead of calling get().

For example:

import multiprocessing as mp
import time

def foo_pool(x):
    time.sleep(2)
    return x*x

result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)

def apply_async_with_callback():
    pool = mp.Pool()
    for i in range(10):
        pool.apply_async(foo_pool, args = (i, ), callback = log_result)
    pool.close()
    pool.join()
    print(result_list)

if __name__ == '__main__':
    apply_async_with_callback()
may yield a result such as

[1, 0, 4, 9, 25, 16, 49, 36, 81, 64]
Notice, unlike pool.map, the order of the results may not correspond to the order in which the pool.apply_async calls were made.

So, if you need to run a function in a separate process, but want the current process to block until that function returns, use Pool.apply. Like Pool.apply, Pool.map blocks until the complete result is returned.

If you want the Pool of worker processes to perform many function calls asynchronously, use Pool.apply_async. The order of the results is not guaranteed to be the same as the order of the calls to Pool.apply_async.

Notice also that you could call a number of different functions with Pool.apply_async (not all calls need to use the same function).

In contrast, Pool.map applies the same function to many arguments. However, unlike Pool.apply_async, the results are returned in an order corresponding to the order of the arguments

'''