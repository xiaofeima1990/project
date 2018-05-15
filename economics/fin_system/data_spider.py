# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 22:26:04 2017

@author: guoxuan

web spider for finance sina 
从新浪网上爬取相关的公司财务信息

"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import time 
'''
get the inquiry url 

basic url + key info + page 

'''
INQUIRY_CAT={
             '1':'profit',
             '2':'operation',
             '3':'grow',
             '4':'debtpaying',
             '5':'cashflow',
             '6':'mainindex',
             '7':'performance',
             '8':'news',
             '9':'incomedetail'
             
             
             }

INDUSTRY_CAT={
'玻璃行业':'new_blhy',
'传媒娱乐':'new_cmyl',
'船舶制造':'new_cbzz',
'电力行业':'new_dlhy',
'电器行业':'new_dqhy',
'电子器件':'new_dzqj',
'电子信息':'new_dzxx',
'发电设备':'new_fdsb',
'纺织机械':'new_fzjx',
'纺织行业':'new_fzhy',
'飞机制造':'new_fjzz',
'服装鞋类':'new_fzxl',
'钢铁行业':'new_gthy',
'公路桥梁':'new_glql',
'供水供气':'new_gsgq',
'化工行业':'new_hghy',
'化纤行业':'new_hqhy',
'环保行业':'new_hbhy',
'机械行业':'new_jxhy',
'家电行业':'new_jdhy',
'家具行业':'new_jjhy',
'建筑建材':'new_jzjc',
'交通运输':'new_jtys',
'酒店旅游':'new_jdly',
'开发区':'new_kfq',
'煤炭行业':'new_mthy',
'摩托车':'new_mtc',
'酿酒行业':'new_ljhy',
'农林牧渔':'new_nlmy',
'农药化肥':'new_nyhf',
'汽车制造':'new_qczz',
'商业百货':'new_sybh',
'食品行业':'new_sphy',
'水泥行业':'new_snhy',
'塑料制品':'new_slzp',
'陶瓷行业':'new_tchy',
'物资外贸':'new_wzwm',
'医疗器械':'new_ylqx',
'仪器仪表':'new_yqyb',
'印刷包装':'new_ysbz',
'造纸行业':'new_zzhy',
'石油行业':'new_syhy',
'综合行业':'new_zhhy',
'金融行业':'new_jrhy',
'房地产':'new_fdc',
'其它行业':'new_qtxy',
'生物制药':'new_swzz',
'有色金属':'new_ysjs',
"":""
              
              }
              
REGION={
        'diyu_1100':'北京',
'diyu_1200':'天津',
'diyu_1300':'河北',
'diyu_1400':'山西',
'diyu_1500':'内蒙古',
'diyu_2100':'辽宁',
'diyu_2200':'吉林',
'diyu_2300':'黑龙江',
'diyu_3100':'上海',
'diyu_3200':'江苏',
'diyu_3300':'浙江',
'diyu_3400':'安徽',
'diyu_3500':'福建',
'diyu_3600':'江西',
'diyu_3700':'山东',
'diyu_4100':'河南',
'diyu_4200':'湖北',
'diyu_4300':'湖南',
'diyu_4400':'广东',
'diyu_4401':'广州',
'diyu_4410':'深圳',
'diyu_4500':'广西',
'diyu_4600':'海南',
'diyu_5100':'四川',
'diyu_5200':'贵州',
'diyu_5300':'云南',
'diyu_5400':'西藏',
'diyu_5500':'重庆',
'diyu_6100':'陕西',
'diyu_6200':'甘肃',
'diyu_6300':'青海',
'diyu_6400':'宁夏',
'diyu_6500':'新疆'

        }


QUARTER={
         '1':'一季报',
         '2':'中报',
         '3':'三季报',
         '4':'年报'
         }
              

URL_basic_fin='http://vip.stock.finance.sina.com.cn/q/go.php/vFinanceAnalyze/kind/'

             
URL_suffix="/index.phtml"





detail_info={
             's_i':'',
             's_a':'',
             's_c':'',
             'reportdate':'',
             'quarter':'',
             'num':'60',
             'p':''
             
             }
             
             
             
             
def get_fundamental_data(report_type="",industry="",year='',quarter='',pause=0.01):
    if len(report_type) >0:
        
        URL_combine=URL_basic_fin+INQUIRY_CAT[str(report_type)]+URL_suffix
        detail_info['s_i']=INDUSTRY_CAT[industry]
        detail_info['reportdate']=str(year)
        detail_info['quarter']=QUARTER[str(quarter)]
        flag=1
        page=1        
        while flag>0:
            time.sleep(pause)
            detail_info['p']=page
            try:
                text = requests.get(URL_combine,params=detail_info).content
                text = text.decode('gbk')
                soup = BeautifulSoup(text,"lxml")
                list_table=soup.find(class_='list_table')
                data_content_t = [tr.text.split("\n") for tr in list_table.find_all('tr')]
                data_content=pd.DataFrame(data_content_t[1:],columns=data_content_t[0])
                
                if page==1:
                    pd_data=data_content.copy(deep=True)
                else:
                    pd_data=pd_data.append(data_content)
                    
                end_flag=soup.find_all(class_='page nolink')
                for ele in end_flag:
                    if "下一页" in ele.text:
                        flag=0
                
                page=page+1
            
            except Exception as e :
                  
                  print(e)
        col=list(pd_data.columns)
        idx = [i for i, x in enumerate(col) if x == '']
        pd_data = pd_data.drop(pd_data.columns[idx], 1)
        return pd_data
                  


 