
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
import sys ,os
# from pandas import Series,DataFrame
import urllib
import hashlib
import requests
import math
import re
import json
import copy

'''
## 数据载入

fhandle=open('url.txt','r')
url_content=fhandle.readlines()
fhandle.close()
sub_url_content=[]

pattern = re.compile("(\.*)(&sn.*)")
for i in range(len(url_content)):
    url_content[i]=re.search("(.*)(&sn.*)",url_content[i]).group(1)
    url_content[i]=re.search("(http://a.*)(/.*)",url_content[i]).group(2)

fhandle=open('url2.txt','w')
for ele in url_content:
    fhandle.write(str(ele)+'\n')
fhandle.close()



数据载入

gis_df=pd.read_csv('2014-1-7.txt',sep='\t')
df.drop(df.columns[],axis=1)


整理数据


#gis_dff=gis_df[[u'电子监管号',u'\ufeff行政区',u'项目位置']]
#col_name_fm=[u'电子监管号',u'\ufeff行政区',u'项目位置']
#gis_name_fm=[u'ID','district','address']
#
#gis_dff.rename(columns=dict(zip(col_name_fm,gis_name_fm)),inplace=True)
'''


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

  
def merge_data(year,f_name_cat,col_name,gis_name,sheet='Sheet1'):
    
    file_list=f_name_cat[year]
    count=0
    for file_ele in file_list:

        print(file_ele)
        temp_data_df = pd.read_excel(path+file_ele,sheet)
        print(temp_data_df.shape)
        
        df_col=temp_data_df.columns
#        temp_data_df.rename(columns={df_col[0]:'行政区'},inplace=True)
#        temp_data_df.drop(temp_data_df.columns[21:],axis=1,inplace=True)
        ######
        # merge data
        ######
        if count==0:
            data_df=temp_data_df
        else:
            data_df=data_df.append(temp_data_df,ignore_index=True)

        count+=1
        
        
           

    data_geo=data_df[col_name]
    data_geo.rename(columns=dict(zip(col_name,gis_name)),inplace=True)
    data_geo[['district','ID','address']].fillna('',inplace=True)
    data_geo.loc[:,['district','ID','address']]=data_geo[['district','ID','address']].fillna('')
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
    'address': u'&address=',
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
        query_info+=dict_convert[ele] + data[ele]

    query_info=dict_convert['preffix']+query_info+dict_convert['suffix']
#    query_info.fillna("",inplace=True)
    
    return query_info


def info_get(api_link):
    flag=4    
    while flag >= 0:
        flag -=1
        try:
            req = requests.get(api_link,timeout=20)
            content=req.json()
            
            if content['status']==0:
                result = content[u'result']
                cofind=result[u'confidence']
                level=result['level']
                location = result[u'location']
                x = location[u'lat']
                y = location[u'lng']
                print (x,y,cofind,level)
                return (x,y,cofind,level)
        except Exception as e :
            print('error get gis')
            break
            
    
    return ('','','','')





if __name__ == '__main__':
    path='F:\\DATAbase\\land\\fm_land\\'
    path2='F:\\DATAbase\\land\\gis_result\\'

    path=input("please input the data position path (eg F:\\land\\)")
    path2=input("please input data output path (eg F:\\gis_result)")
    sub_url_content=[]
    cat_files=datafile_cate(path)
#    col_name=['行政区','电子监管号','项目位置','土地用途','行业分类','成交价格(万元)','面积(公顷)','合同签定日期','土地使用年限']
#    gis_name=['district','ID','address','land_usage','industry_cat','price','area','date','year']
    id_name=input('please input the data ID name')    
    col_name=['county',id_name,'address','usage','price','area','date','duration']
    gis_name=['district','ID','address','land_usage','price','area','date','year']
    year=input('type in the year you want ')
    (gis_df,land_df)=merge_data(year,cat_files,col_name,gis_name)
    
    
    query_info=convert(gis_df)
    geo_link=baidu_gis(query_info)
    
    gis_link=pd.DataFrame(columns=['ID','api_link'])
    gis_link['ID']=gis_df['ID']
    gis_link['api_link']=geo_link    
    
    '''
    拆分
    '''
    for i in range(0,len(geo_link),100):
        sub_url_content.append(gis_link.loc[i:i+100])
    
    '''
    ---------------------------
    single 
    ---------------------------
    
    
    '''
    
    column_name=['ID','lat','lng','confidence','level']
    result_gis_df=pd.DataFrame(columns=column_name)
    for num, api_links in enumerate(sub_url_content[686:]):
        result_df=pd.DataFrame(columns=column_name)
        for i in range(len(api_links)):
            
#            if req.json()['status']==0:
            gis_info=info_get(api_links.iloc[i,1])
#                result_df.loc[i]=gis_info
            result_df.loc[i,'ID']=copy.deepcopy(api_links.iloc[i,0])
            result_df.loc[i,['lat','lng','confidence','level']]=gis_info
                
#            else:
#                result_df.loc[i,'ID']=copy.deepcopy(api_links.iloc[i,0])
#                result_df.loc[i,['lat','lng','confidence','level']]=('','','','')
                
        result_gis_df=result_gis_df.append(result_df,ignore_index=True)
        filename=path2+year+'_gis.csv'
        if not os.path.isfile(filename):
            result_df.to_csv(filename,mode='w',header=True) 
            # 加上 总的dataframe 一起
        else:
            result_df.to_csv(filename,mode='a',header=False)
        
    result_final_df=pd.merge(land_df, result_gis_df, left_on=id_name, right_on='ID', how='inner')
    result_final_df.to_csv(path2+year+'-df.csv',header=True,sep='\t')            
    if not os.path.isfile(filename):
        result_final_df.to_csv(path2+year+'-df.csv',header=True,sep='\t',mode='w',index=False) 
    # 加上 总的dataframe 一起
    else:
        result_final_df.to_csv(path2+year+'-df.csv',header=True,sep='\t',mode='a',index=False) 
    
    
    





















#
#import queue
#import threading
#import time
#import copy, sys 
#
#exitFlag = 0
#tn=20
#print('we are dealing with: %s' %flag)
#
#headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'}
#req=[]
#GIS_result=[]
#fail_link=[]
#class myThread (threading.Thread):
#    def __init__(self, threadID, name, q):
#        threading.Thread.__init__(self)
#        self.threadID = threadID
#        self.name = name
#        self.q = q
#        self.header={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}
#    def run(self):
#        print("Starting " + self.name)
#        process_data(self.name, self.q,self.header)
#
#def process_data(threadName, q, header):
#    while not exitFlag:
#        queueLock.acquire()
#        if not workQueue.empty():
#            data = q.get()
#            try: 
#                req = requests.get(data)
##                 print(req.json())
#                if req.json()[u'status']==211:
#                    print("error occur")
#                    time.sleep(1)
#                    req = requests.get(data)
#                    print(req.json())
#                if req.json()[u'status']==211:
#                    time.sleep(1)
#                    req = requests.get(data)
#                    print(req.json())
#                try:
#                    content = req.json()
#                    result = content['result']
#                    location = result['location']
#                    x = location['lat']
#                    y = location['lng']
#                    temp_result=(x,y,result['confidence'])
#                    GIS_result.append(copy.deepcopy(temp_result))
#                except: 
#                    temp_result=("","","")
#                    GIS_result.append(copy.deepcopy(temp_result))
#            except :
#                fail_link.append(data)
#                temp_result=("-","-","-")
#                GIS_result.append(copy.deepcopy(temp_result))
#            
#            queueLock.release()
#            print("%s processing:  %s" % (threadName, temp_result))
#        else:
#            queueLock.release()
#        time.sleep(1)
#
#threadList = ["T1", "T2", "T3","T4"]
#queueLock = threading.Lock()
#fm_url=[]
#
#
#
#workQueue = queue.Queue(tn)
#threads = []
#threadID = 1
#
## 创建新线程
#for tName in threadList:
#    print("create thread")
#    thread = myThread(threadID, tName, workQueue)
#    thread.start()
#    threads.append(thread)
#    threadID += 1
#
## 填充队列
#queueLock.acquire()
#for word in geo_link[:tn]:
#    workQueue.put(word)
#queueLock.release()
#
## 等待队列清空
#while not workQueue.empty():
#    pass
#
## 通知线程是时候退出
#exitFlag = 1
#
## 等待所有线程完成
#for t in threads:
#    t.join()
#print("Exiting Main Thread")
#
#GIS_df=pd.DataFrame(GIS_result,columns=['lat','lng','confidence'])
#print(GIS_df)
#
#print("the num of empty GIS is : ")
#print(len(GIS_df[GIS_df['lat']==""]))
#
#GIS_ind=pd.concat([data_geo,GIS_df],axis=1)
#
#
#
#if flag=='sm':
#    ## save the result in the total info data
#    cand_col_sm=['mindex',u'县',u'地址',u'剩余年限',u'面积',u'转让费',u'容积率']
#    sm_GIS=pd.concat([sm_df[cand_col_sm],GIS_df],axis=1)
#
#else:
#    ## save the result in the  data
#    cand_col_fm=['mindex',u'行政区',u'项目位置',u'土地使用年限',u'面积(公顷)',u'成交价格(万元)',u'约定容积率上限']
#    sm_GIS=pd.concat([fm_df[cand_col_fm],GIS_df],axis=1)
#
#
## In[ ]:
#
#GIS_ind=pd.concat([data_geo,GIS_df],axis=1)
#GIS_ind
#
#
#GIS_ind.to_excel(path+'GIS_fm.xlsx','fm')
#GIS_ind.to_excel(path+'GIS_fm.xlsx','fm')

