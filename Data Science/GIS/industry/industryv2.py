
# coding: utf-8

# # 工业土地地理位置信息获取
# 
# * 有两种格式，需要分别处理
# * 当地址信息不全时，需要利用县镇数据进行处理
# * 多进程进行信息获取与多线程信息获取比较
# 
# 

# In[1]:


import pandas as pd
import numpy as np
import sys 
# from pandas import Series,DataFrame
import urllib
import hashlib
import requests
import math
import re
import json
import copy
import os


# In[2]:
path='E:\\data\\demo\\'
nan=np.nan
def datafile_cate():
    savefile=[]
    read_file_list =os.listdir(path)
    
    for element in read_file_list:
        savefile.append(os.path.splitext(os.path.basename(element)))
    
    
    
    # year=savefile[1][0].split('-')
    # year[0]
    f_year=set()
    temp_list=[]
    f_name_cat={}
    for ele in savefile:
    #     print(ele)
        year=ele[0].split('-')[0]
        f_year.add(year)
    # f_year
    # temp_list
    for ele in f_year:
        for ele2 in savefile:
            if ele in ele2[0]:
                temp_list.append(ele2[0]+ele2[1])    
        f_name_cat[ele]=copy.copy(temp_list)
        temp_list=[]
    
    return f_name_cat
    
def merge_data(year,f_name_cat):
    
    file_list=f_name_cat[year]
    count=0
    for file_ele in file_list:

        print(file_ele)
        temp_data_df = pd.read_excel(path+file_ele)
        print(temp_data_df.shape)
        ######
        # merge data
        ######
        if count==0:
            data_df=temp_data_df
        else:
            data_df=data_df.append(temp_data_df,ignore_index=True)

        count+=1
        
        
        
        
        ### -------------------------------
        ##  这里是在1999年以后的东西进行的，不是之前的情况
        ### ------------------------------
        
        
        data_geo=data_df[[u'法人代码', u'法人单位', u'地址代码',u'省份',u'市',u'县',u'乡（镇）', u'村（街、门牌号）',u'街道办事处']]
        data_geo=data_geo.reset_index()
        data_geo.drop('index', axis=1, inplace=True)
        print(data_geo.shape)
        print(data_geo.columns)
        
        # combine into 地址
        li=['乡（镇）', '村（街、门牌号）','街道办事处']
        ss=''
        for ele in li:
            data_geo[ele].fillna('',inplace=True)
            ss+=data_geo[ele]
        data_geo['地址']=ss
        
        col_name=['法人代码','法人单位','省份','市','县','地址']
        gis_name=['ID','title','province','city','district','address']
        data_geo=data_geo[col_name]
        data_geo.rename(columns=dict(zip(col_name,gis_name)),inplace=True)        
    return data_geo        
        
def get_query_link(data_geo,gis_name,ID=None):
    
    query_info=convert(data_geo[gis_name])
    geo_link=baidu_gis(query_info)
    ID_list=list(data_geo['ID'])
    
    return zip(ID_list,geo_link)




def baidu_gis(queryStr):
    '''
    queryStr 包括了请求百api的url 地址
    以get请求为例http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=yourak
    并且对url 转码 除了保留字符不转换，其余要进行转码加密
    
    '''
    
    api_link=[]
    # 对queryStr进行转码，safe内的保留字符不转换
    for ele in queryStr:
        encodedStr=urllib.parse.quote(ele, safe="/:=&?#+!$,;'@()*[]")
        # 在最后直接追加上yoursk
        rawStr = encodedStr + 'DTtxldoesco94o9YZT3RuGlKarBGr7Xv'

        sn = hashlib.md5(urllib.parse.quote_plus(rawStr).encode('utf-8')).hexdigest()

        api_link.append('http://api.map.baidu.com'+ele+"&sn="+sn)
        
        
    return api_link


# In[ ]:

dict_convert={
    'preffix':'/geocoder/v2/?',
    'suffix':'&output=json&ak=9gTAEoFWvBoKHl3u3dFp5ff7',
    'title': u'title=',
    'address': u'&address=',
    'province': u'&province=',
    'city': u'&city=',
    'district': u'&disctrict='    
}
key_id_list=['title','address','province','city','district']


def convert(data):
    '''
    data is a dataframe format saving the 
    info of geo info
    
    '''
    
    row,col=data.shape
    query_info=''
    for ele in data.columns:
        query_info+=dict_convert[ele] + data[ele]

    query_info=dict_convert['preffix']+query_info+dict_convert['suffix']
    query_info.fillna("",inplace=True)
    
    return query_info
    



import multiprocessing
import copy,time
tn=20

class work_process(multiprocessing.Process):
    def __init__(self, task_queue, result_queue,fail_link,lock):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.fail_link=fail_link
        self.lock=lock

    def run(self):
        proc_name = self.name
        while True:
            data = self.task_queue.get()
            if data is None:
                # Poison pill means shutdown
                print ('%s: Exiting' % proc_name)
                self.task_queue.task_done()
                break
            # self.lock.acquire()
            result=process_GIS(data)
            self.task_queue.task_done()
            # self.lock.release()
#            print('%s: %s' % (proc_name, result[0])
#            print('%s on the process' %proc_name)
#            self.result_queue.put(result)
            self.result_queue.put(copy.deepcopy(result))
            with open('temp.txt','a+') as f:
                temp=''
                for ele in result:
                    temp+=str(ele)+'\t'
                temp+='\n'
                f.write(temp)
                
            if np.isnan(result[2]):
                self.fail_link.put(data)            
    
        print('proces is done %s' % proc_name)
        return
        
def work():
    print('working on process')

def process_GIS(data):
#    print('working on GIS')
    ID=data[0]
    link=data[1]
    try: 
        req = requests.get(link)
#                 print(req.json())
        if req.json()[u'status']==211:
            print("error occur")
            time.sleep(1)
            req = requests.get(data)
#             print(req.json())
        if req.json()[u'status']!=0:
            time.sleep(1)
            req = requests.get(data)
        try:
            content = req.json()
            result = content['result']
            location = result['location']
            x = location['lat']
            y = location['lng']
            temp_result=(ID,x,y,result['confidence'])
        except: 
            temp_result=(ID,nan,nan,nan)
    except :
#        fail_link.append(data)
        temp_result=(ID,nan,nan,nan)
#        GIS_result.append(copy.deepcopy(temp_result))

    return temp_result


if __name__ == '__main__':
    GIS_result=[]
    path='.\\demo\\'
    path_new='.\\save\\'
    f_name_cat=datafile_cate()
    data_geo=merge_data('2004',f_name_cat)
    gis_name2=['district','address']
#    data_query=get_query_link(data_geo,gis_name2)
    query_info=convert(data_geo[gis_name2])
    geo_link=baidu_gis(query_info)
    ID_list=list(data_geo['ID'])
    data_query=zip(ID_list,geo_link)
    # Establish communication queues
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()
    fail_link = multiprocessing.JoinableQueue()
    lock = multiprocessing.Lock()  
    # Start consumers
    num_cpu = multiprocessing.cpu_count()
    print ('maximum process %s' % num_cpu)
    record_process = [ work_process(tasks, results,fail_link,lock)
                 for i in range(4) ]
    for w in record_process:
        w.daemon = True
        w.start()
   
   # Enqueue jobs
    for word in data_query:
#        print(word)        
        tasks.put(word)


    print(tasks.qsize())
   
   # Add a poison pill for each consumer
    for i in range(4):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()
    
    # for w in record_process:
    #     w.join()
    
    
    print('task done ')
    starttime = time.time()
    # Start printing results
    for i in range(results.qsize()): 
        
        result = results.get()
        print ('Result:', result)
        GIS_result.append(copy.deepcopy(result))


    GIS_df=pd.DataFrame(GIS_result,columns=['ID','lat','lng','confidence'])
    GIS_df.set_index('ID')
#    print(GIS_df)    
    print("the num of empty GIS is : ")    
    print(len(np.isnan(GIS_df['lat'])))
#    
#    
    if fail_link.qsize()>10:
        print('re start again ')        
        gis_name3=['district','address']
#        data_query=get_query_link(data_geo,gis_name3)
        flag=5
        
        while flag>0:
            flag-=1
            #####
            # add geo adustment to the data
            #####
            GIS_result=[]
            tasks=fail_link
            fail_link = multiprocessing.JoinableQueue()
            results = multiprocessing.Queue()
            # Start consumers
            num_cpu = multiprocessing.cpu_count()
            print ('maximum process %s' % num_cpu)
            record_process = [ work_process(tasks, results,fail_link,lock)
                         for i in range(4) ]
            for w in record_process:
                w.start()

            # Add a poison pill for each consumer
            for i in range(4):
                tasks.put(None)

            # Wait for all of the tasks to finish
            tasks.join()

            print('task done ')
            
            if fail_link.qsize()<10:
                break
            for i in range(results.qsize()): 
                result = results.get()
                print ('Result:', result)
                if not np.isnan(result[2]):
                    GIS_result.append(copy.deepcopy(result))


            GIS_df2=pd.DataFrame(GIS_result,columns=['ID','lat','lng','confidence'])
            GIS_df2.set_index('ID')
            GIS_df.update(GIS_df2, join = 'left', overwrite = True)
#            GIS_df.loc[GIS_df['lat']=="-",['lat','lng','confidence']]=GIS_df2['lat','lng','confidence']
#
#

#-----------------------
# save the data
#-----------------------

    # GIS_ind=pd.concat([data_geo,GIS_df],axis=1)
    GIS_df.to_excel(path+'2004-f'+'.xlsx','sheet1')
    endtime = time.time()
    total_time=(endtime-starttime)/3600.0
    print('total time:%f h' % total_time)       



#
#In[100] : df = pd.merge(df1, df2, how='left', on=['filename','m'])
#
#In[101] : df
#Out[101]: 
#    filename   m   n_x  n_y
#0  test0.dat  12  None  NaN
#1  test2.dat  13  None   16
#
#In[102] : df['n'] = df['n_y'].fillna(df['n_x'])
#
#In[103] : df = df.drop(['n_x','n_y'], axis=1)
#
#In[104] : df
#Out[104]: 
#    filename   m     n
#0  test0.dat  12  None
#1  test2.dat  13    16