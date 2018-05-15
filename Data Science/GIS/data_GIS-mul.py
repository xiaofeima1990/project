
# coding: utf-8

'''
# # 土地经纬度信息获取
# 
# 本程序目的在于方便进行大批量地理位置信息转换，从地址信息转换成经纬度。具体信息可参考LBS百度云。
# 
# 操作方式如下：
# 
# 1. 原始数据中提取所需要的地址信息，行政区信息（县、省等）
# 2. 把相关地址信息和行政区信息导入到info_data中
# 3. 运行程序，输出两个结果，第一个为地理位置信息的dataframe,第二个则为出错信息的list.
# 
# 错误与获取信息失败的处理：
# 
# * 出错信息用"-"表示，返回无效地址为：""
# * "-"可以进行再次尝试,fail_list2 中存储了"-"
# * ""可以进行再次尝试,fail_list 中存储了""
# 
# ## 程序解释
# 
# * 函数baidu_gis是进行信息查询的预先处理，遵循LBS百度云api接口相关规定，主要进行密钥加密 （中文编码是一个急需解决的大问题）
# * 源数据存储在hdf5格式中，通过pandas 的支持函数读写。 相关问题可以查看hdf5 文件说明
# * 
# 

--------------------------

一般步骤：
先 convert 
再 baidu_gis
再 request.get 
末 get_info

'''

import pandas as pd
import numpy as np 
# from pandas import Series,DataFrame
import urllib
import hashlib
import requests
import re,os
import json
import multiprocessing as mp
import time 
from datetime import date, timedelta,datetime
import copy

pd.set_option('chained_assignment',None)



def datafile_cate(path):
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

  
def merge_data(year,f_name_cat,sheet='Sheet1'):
    
    file_list=f_name_cat[year]
    count=0
    for file_ele in file_list:

        print(file_ele)
        temp_data_df = pd.read_excel(path+file_ele,sheet)
        print(temp_data_df.shape)
        temp_data_df.drop(temp_df.columns[21:],axis=1,inplace=True)
        ######
        # merge data
        ######
        if count==0:
            data_df=temp_data_df
        else:
            data_df=data_df.append(temp_data_df,ignore_index=True)

        count+=1
        
        
           
        col_name=['行政区','电子监管号','项目位置','土地用途','行业分类','成交价格(万元','面积(公顷)','合同签定日期','土地使用年']
        gis_name=['district','ID','address','land_usage','industry_cat','price','area','date','year']
        data_geo=data_df[col_name]
        data_geo.rename(columns=dict(zip(col_name,gis_name)),inplace=True)        
    return (data_geo,data_df)  



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



dict_convert={
    'preffix':'/geocoder/v2/?',
    'suffix':'&output=json&ak=9gTAEoFWvBoKHl3u3dFp5ff7',
    'title': u'title=',
    'address': u'&address=',
    'province': u'&province=',
    'city': u'&city=',
    'district': u'&disctrict='    
}
key_id_list=['address','district']


def convert(data):
    '''
    data is a dataframe format saving the 
    info of geo info
    
    '''
    
    (row,col)=data.shape
    query_info=''
    for ele in key_id_list:
        if 'ID' not in ele:
            query_info+=dict_convert[ele] + data[ele]

    query_info=dict_convert['preffix']+query_info+dict_convert['suffix']
    query_info.fillna("",inplace=True)
    
    return query_info

column_name=['ID','lat','lng','confidence','level']

def info_get(api_links,file_name):
    
#    print (x,y,cofind,level)
    result_df=pd.DataFrame(columns=column_name)
    
    try:    
        for i, row in api_links.iterrows():
            try:
                req = requests.get(row[1])
                if req.json()['status']==0:
                    result = req.json()[u'result']
                    cofind=result[u'confidence']
                    level=result['level']
                    location = result[u'location']
                    x = location[u'lat']
                    y = location[u'lng']
        
                    
                    result_df.loc[i,['lat','lng','confidence','level']]=copy.deepcopy([x,y,cofind,level])
    #                result_df.loc[i,'ID']=copy.deepcopy(api_links.loc[i,'ID'])
                    result_df.loc[i,'ID']=copy.deepcopy(row[0])
        #                        print(file_name)
                else:
                    result_df.loc[i,['lat','lng','confidence','level']]=copy.deepcopy(('','','',''))
                    result_df.loc[i,'ID']=copy.deepcopy(api_links.loc[i,'ID'])
                
            except Exception as e :
                    print('error',e)
                    result_df.loc[i,['lat','lng','confidence','level']]=copy.deepcopy(('','','',''))
                    result_df.loc[i,'ID']=copy.deepcopy(api_links.loc[i,'ID'])
            
         
            
    except (KeyboardInterrupt, SystemExit):
        
        print('keyboard Interrupt')
    
    finally:     
        if not os.path.isfile(file_name+'.csv'):
            result_df.to_csv(file_name+'.csv',mode='w',header=True)
        else:
            result_df.to_csv(file_name+'.csv',mode='a',header=False) 


'''
---------------------------
multiprocess 
---------------------------


'''


            

def parall_work(work_queue,lock,ID,file_name):
       
    while True: 
        if not work_queue.empty():
            api_links = work_queue.get()
#            lock.acquire()
            print(work_queue.qsize())
            print("------"+str(ID)+"sub process is running"+"------")
#            lock.acquire()
            info_get(api_links, file_name)
#            lock.release()           
            work_queue.task_done() 
        else: 
            print("task is empty")
            break
                
#    except (KeyboardInterrupt, SystemExit):
#        lock.acquire()
#        if not os.path.isfile(file_name):
#            result_df.to_csv(file_name+'.csv',mode='w',header=True)
#        else:
#            result_df.to_csv(file_name+'.csv',mode='a',header=False)
#        lock.release()
#        print("interrupt the keyboard")
            
                              
    print('----done----')


def input_workqueu(work_queue,fele,path):
    
    

    '''
    数据载入
    '''
    suffix='.txt'
    gis_df=pd.read_csv(path+fele+suffix,sep='\t')
      
    '''
    整理数据
    '''
    
    gis_dff=gis_df[[u'电子监管号',u'行政区',u'项目位置']]
    col_name_fm=[u'电子监管号',u'行政区',u'项目位置']
    gis_name_fm=[u'ID','district','address']
    
    gis_dff.rename(columns=dict(zip(col_name_fm,gis_name_fm)),inplace=True)

    query_info=convert(gis_dff)
    geo_link=baidu_gis(query_info)
    
    gis_link=pd.DataFrame(columns=['ID','api_link'])
    gis_link['ID']=gis_dff['ID']
    gis_link['api_link']=geo_link
    
    '''
    拆分
    '''
    sub_url_content=[]
    interval=100
    for i in range(0,len(gis_link),interval):
        sub_url_content.append(gis_link.loc[i:i+interval-1])

    for data in sub_url_content:
        work_queue.put(data)
    
    
#def output_error_link(error_queue,date_start,date_end):
#    filename=str(date_start.year) +"-"+ str(date_start.month)+"_"+str(date_end.year)+"-"+str(date_end.month)
#    if not os.path.isfile(filename):
#        fhandle=open(filename+'.csv','w')
#    else:
#        fhandle=open(filename+'.csv','a')
#    
#    while True:
#        if not error_queue.empty():
#            url_txt=error_queue.get()
#            fhandle.write(str(url_txt).rstrip()+"\n")
#        else:
#            break
#    
#    fhandle.close()
#    print("save the error link")



 
    
    path=".\\gis\\"

    wait_file_date=[]
    savefile=[]
    savefile_date=[]
    read_file_list=[]

     
    manager = mp.Manager()
    lock  = manager.Lock()

    read_file_list =os.listdir(path)
    #read_file_list = glob.glob('.\\url\\*.txt')
    print(read_file_list)
    for element in read_file_list:
        savefile.append(os.path.splitext(os.path.basename(element)))
        savefile_date.append(datetime.strptime(os.path.splitext(os.path.basename(element))[0],'%Y-%m-%'))
        
    date_start="2014-1-1"
    date_end="2014-1-10"
    date_start=datetime.strptime( date_start, '%Y-%m-%d')
    date_end=datetime.strptime( date_end, '%Y-%m-%d')
    
#    input_error_recover=input("start infor getting error recover 0=no, 1=yes ")
#    if input_error_recover=="1":
#        error_info=recover_info()
#    else:
#        date_start= input("Please enter query start date (YYYY-M-D,no zeros needed)?")
#        date_end=input("Please enter query end date (YYYY-M-D,no zeros needed)?")
#        print(date_start,date_end)
#        date_start=datetime.strptime( date_start, '%Y-%m-%d')
#        date_end=datetime.strptime( date_end, '%Y-%m-%d')
#        
        # normal running 
        
    for element in savefile_date:
        if element >=date_start and element <= date_end: 
            wait_file_date.append(element)

    # Establish communication queues
    tasks = manager.Queue()
    

    if len(wait_file_date)<1:
        print("current date range has no new info, please select another one ")
        # wait to continue
    else:
        for fele in wait_file_date:
            fele=fele.strftime("%Y-X%m-X%d").replace('X0','X').replace('X','')
            fele=str(fele)
            input_workqueu(tasks,fele,path)
            print('queue num is ', tasks.qsize())
            num_cpu = mp.cpu_count()
            print('maximum process %s' % num_cpu)
            num_process=2
            pool = mp.Pool(processes=4)
            
            result_filename=str(fele)+'-gis'
            try:
                
                print("start pool")
                for i in range(num_process):
                    print(str(i)+" process" )
                    pool.apply_async(parall_work, (tasks,lock,i,result_filename))
                
                pool.close()
                        
        #        parall_work(driver,tasks,lock,error)
                
                pool.join()
                print("pool work is finished")
                
                print("process is done")
            except Exception as ex:
                print("error",Exception,":",ex)
        


