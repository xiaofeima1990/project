#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 11:58:02 2023

@author: xiaofeima

公拍网 https://pmsearch.jd.com/?publishSource=7&childrenCateId=12728

"""


from requests_html import HTMLSession,AsyncHTMLSession
import pandas as pd
import re
from sys import platform
# path 
if platform == "win32":
    path_prefix = "D:/"
else:
    path_prefix = "/Users/xiaofeima/"
    
path = path_prefix + "Dropbox/work/UIBE/global_production/"
output = path

session = HTMLSession()
base_url = "https://pmsearch.jd.com/?publishSource=7&childrenCateId=12728"
start_page = 1
raw = session.get(base_url)
print(raw.status_code)

raw.html.render(sleep = 3)