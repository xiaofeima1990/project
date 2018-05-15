# -*- coding: utf-8 -*-
"""
Created on Tue May 31 10:37:04 2016

@author: xiaofeima

law_spider run

this script is the main running profile
"""

from law_spider import *
from spider_database import * 
import time,datetime
import copy

'''
VARIABLES and PARAMETERS
'''
abs_info_dict={
"label1":"text",
"label2":"text",
"label":"text",
"title":"text" ,
"href":"text",
"court":"text",
"ID":"text",
"date":"text",
"content":"text",
"ID_key":"integer primary key ",
}

href_dict={
"ID_key":"integer primary key",
"href":"text",

}

full_content_info_dict={
"ID_key":"integer primary key",
"full_content":"text",
"title":"text" ,
"data":"text"
}

URL="http://wenshu.court.gov.cn/list/list/?sorttype=1"
FILE_TYPE="判决书"
YEAR="2007"
show_number=20
search_dict={'文书类型':'判决书',
             '裁判年份':'2007',
             '一级案由':'行政案由'}


'''
spider link process
'''




def rolling_info_get(spider_link,abs_info_database,link_database,year,split_flag,time_span=15):        
    search_dict={'文书类型':'判决书',
         '裁判年份':year,
         '一级案由':'行政案由'}
    
    if split_flag==0:
        t_count=1
        spider_link.set_search_url(search_dict,year)
        spider_link.open_page()
        total_number=spider_link.total_number()
    
        i=1
        while i <= total_number:
            (abs_info_dict_list,href_dict_list)=spider_link.get_abstract_info()
            abs_info_database.save_data(copy.deepcopy(abs_info_dict_list))
            link_database.save_data(copy.deepcopy(href_dict_list))
            save_link(href_dict_list,"","link")
            time.sleep(1)
            i+=1
            t_count+=1
            print("current counting page is %s, accumulate counting page is %s" %(str(i),str(t_count)))
            if t_count>100:
                print('enough need a rest! for 2 h ')
                print('current time is '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                time.sleep(3600*2)
                t_count=1
                print("continue start! ,time is " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if i== total_number:
                print("get the end ")
                break
            else:
                spider_link.next_page()
                
            print('page %s finished' %str(i))
            
            time.sleep(5)
    else:
        t_count=1
        search_dict.pop('裁判年份')
        ## initialize date
        base_date=datetime.datetime(int(year), 1, 1)
        date1=base_date
        date2=base_date+timedelta(days=time_span)
        end_date=datetime.datetime(int(year), 12, 31)
       
        
        while date2<=end_date:
            loop_flag=1
            while loop_flag:
                spider_link.split_time_search(search_dict,date1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d"))
                spider_link.open_page()
                time.sleep(3)
                total_number=spider_link.total_number()
                if total_number<=50:
                    print('start getting info from %s to %s' %(date1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d")))
                    loop_flag=0
                    break
                else:
                    print("still too much, we need split")
                    interval=date2-date1
                    date2=date2-timedelta(days=int(interval.days)/2)
                    if date2<date1 :
                        print("error, the information is too big, we need to start with day by day ")
                        date2=date1+timedelta(days=1)
        
#        for m in range(1,13):
#            begin_date=datetime.datetime(int(year), m, 1)
#            if m<12:
#                end_date=datetime.datetime(int(year), m+1, 1)-timedelta(days=1)
#            else:
#                end_date=datetime.datetime(int(year), m, 31)

               
            i=1
            while i <= total_number:
                (abs_info_dict_list,href_dict_list)=spider_link.get_abstract_info()
                abs_info_database.save_data(copy.deepcopy(abs_info_dict_list))
                link_database.save_data(copy.deepcopy(href_dict_list))
                save_link(href_dict_list,"","link")
                time.sleep(1)
                
                print("current counting page is %s, accumulate counting page is %s" %(str(i),str(t_count)))
                if t_count>100:
                    print('enough need a rest! for 2 h ')
                    print('current time is '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    time.sleep(3600*2)
                    t_count=1
                    print("continue start! ,time is " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                if i== total_number:
                    print("get the end ")
                    break
                else:
                    spider_link.next_page()

                print('page %s finished' %str(i))
                i+=1
                t_count+=1
                
                time.sleep(5)
            
            
            ## loop the date 
            date1 = date2 + timedelta(days=1)
            date2 = date1 + timedelta(days=time_span)
            ## consistent within month 
            if date1 <= end_date and date2 > end_date:
                date2=end_date
            print('----next period from %s to %s' %(date1.strftime("%Y-%m-%d") , date2.strftime("%Y-%m-%d")))
    print("finsih the process")


def info_get_time(spider_link,abs_info_database,link_database,year,date1,date2,split_flag,time_span=15):
    search_dict={'文书类型':'判决书',
         '一级案由':'行政案由'}
         
    t_count=1
    ## initialize date
#    base_date=datetime.datetime(int(year), 1, 1)
    date1=datetime.datetime.strptime( date1, '%Y-%m-%d')
    date2=datetime.datetime.strptime( date2, '%Y-%m-%d')
    end_date=datetime.datetime(int(year), 12, 31)
   
    
    while date2<=end_date:
        loop_flag=1
        while loop_flag:
            spider_link.split_time_search(search_dict,date1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d"))
            spider_link.open_page()
            time.sleep(3)
            total_number=spider_link.total_number()
            if total_number<=50:
                print('start getting info from %s to %s' %(date1.strftime("%Y-%m-%d"),date2.strftime("%Y-%m-%d")))
                loop_flag=0
                break
            else:
                print("still too much, we need split")
                interval=date2-date1
                date2=date2-timedelta(days=int(interval.days)/2)
                if date2<date1 :
                    print("error, the information is too big, we need to start with day by day ")
                    date2=date1+timedelta(days=1)
    
#        for m in range(1,13):
#            begin_date=datetime.datetime(int(year), m, 1)
#            if m<12:
#                end_date=datetime.datetime(int(year), m+1, 1)-timedelta(days=1)
#            else:
#                end_date=datetime.datetime(int(year), m, 31)

           
        i=1
        while i <= total_number:
            (abs_info_dict_list,href_dict_list)=spider_link.get_abstract_info()
            abs_info_database.save_data(copy.deepcopy(abs_info_dict_list))
            link_database.save_data(copy.deepcopy(href_dict_list))
            save_link(href_dict_list,"","link")
            time.sleep(1)
            i+=1
            t_count+=1
            print("current counting page is %s, accumulate counting page is %s" %(str(i),str(t_count)))
            if t_count>100:
                print('enough need a rest! for 2 h ')
                print('current time is '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                time.sleep(3600*2)
                t_count=1
                print("continue start! ,time is " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if i== total_number:
                print("get the end ")
                break
            else:
                spider_link.next_page()
                
            print('page %s finished' %str(i))
            
            time.sleep(5)
        
        
        ## loop the date 
        date1 = date2 + timedelta(days=1)
        date2 = date1 + timedelta(days=time_span)
        ## consistent within month 
        if date1 <= end_date and date2 > end_date:
            date2=end_date
        print('----next period from %s to %s' %(date1.strftime("%Y-%m-%d") , date2.strftime("%Y-%m-%d")))


## initial the class and get prepared 
flag=input("choose the mode recover==1 or new start==0")

link_database=spider_database('spider_link.db')
abs_info_database=spider_database('spider_info.db')
if flag=='0':
    year_list=['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015']
    spider_link=law_spider_link(url=URL,show_number=20)
    for Year in year_list:
        search_dict={'文书类型':'判决书',
                 '裁判年份':Year,
                 '一级案由':'行政案由'}
    
    
        
        link_database.creat_table('link_'+Year,href_dict)
        
        abs_info_database.creat_table('abs_info_'+Year,abs_info_dict)
        
        
        spider_link.set_search_url(search_dict,Year)
        spider_link.open_page()
        total_number=spider_link.total_number()
        split_flag=0
        if total_number>100:
            print("many page numbers, need split")
            split_flag=1
            
        rolling_info_get(spider_link,abs_info_database,link_database,Year,split_flag)
            
        ## get link for single process
#        i=1
#        while i <= total_number:
#            (abs_info_dict_list,href_dict_list)=spider_link.get_abstract_info()
#            abs_info_database.save_data(copy.deepcopy(abs_info_dict_list))
#            link_database.save_data(copy.deepcopy(href_dict_list))
#            save_link(href_dict_list,"","link")
#            time.sleep(1)
#            i+=1
#            print("counting page is "+str(i))
#            if cc>400:
#                print('enough need a rest! ')
#                time.sleep(3600*2)
#                cc=1
#            
#            if i== total_number:
#                print("get the end ")
#                break
#    
#            else:
#                spider_link.next_page()
#                cc+=1
#                
#            print('page %s finished' %str(i))
#            
#            time.sleep(5)
#    

else:
    Year=input('input year')
    page=input('recovering page')
    date1=input("plase input detail begin time eg:2014-01-01, don't need just press no")
    if 'n' not in date1:
        date2=input("plase input detail second span time eg:2014-01-01")
    
    spider_link=law_spider_link(url=URL,show_number=20)
    
    search_dict={'文书类型':'判决书',
                 '裁判年份':Year,
                 '一级案由':'行政案由'}
                 
    spider_link.set_search_url(search_dict,Year)
    
#    link_database=spider_database('spider_link.db')
    link_database.creat_table('link_'+Year,href_dict)
#    abs_info_database=spider_database('spider_info.db')
    abs_info_database.creat_table('abs_info_'+Year,abs_info_dict)
    
    spider_link.open_page()
    total_number=spider_link.total_number()
    i=1
    cc=1
    while i < int(page):
        try:
            spider_link.next_page()
        except:
            print("next page failed")
        i+=1
        cc+=1
        if cc>300:
            print('enough need a rest! for 1 h ')
            print('current time is '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            time.sleep(3600)
            cc=1
        
        time.sleep(5)
        
    split_flag=0
    if total_number>100:
        print("many page numbers, need split")
        split_flag=1
    if 'n' in date1:    
        rolling_info_get(spider_link,abs_info_database,link_database,Year,split_flag)
    else:
        info_get_time(spider_link,abs_info_database,link_database,Year,date1,date2,split_flag)

    
#    while i <= total_number:
#        (abs_info_dict_list,href_dict_list)=spider_link.get_abstract_info()
#        abs_info_database.save_data(copy.deepcopy(abs_info_dict_list))
#        link_database.save_data(copy.deepcopy(href_dict_list))
#        save_link(href_dict_list,"","link")
#        time.sleep(1)
#        i+=1
#        print("counting page is "+str(i))
#        if cc>400:
#            print('enough need a rest! for 2 h ')
#            print('current time is '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#            time.sleep(3600*2)
#            cc=1
#            print("continue start! ,time is " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#        if i== total_number:
#            print("get the end ")
#            break
#
#        else:
#            spider_link.next_page()
#            cc+=1
#            
#        print('page %s finished' %str(i))
#        
#        time.sleep(5)
        
#import multiprocessing as mp


