# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 11:52:34 2018

@author: xiaofeima

API data collecting for crunchbase
user_key=2bddce7174abaf499d47ed2a4baf4581
This script will help to track what kinds of data do I need
And plan for the data extraction

"""
import requests
import pandas as pd
import copy, time
import sqlite3
import json

payload = {'user_key': '2bddce7174abaf499d47ed2a4baf4581'}

url = "https://api.crunchbase.com/v3.1/organizations/62571438893bae131828a57ece7a0b06" 

url = "https://api.crunchbase.com/v3.1/people/a4c76c4940e44a79b1dcea1d00c71645" 

url = "https://api.crunchbase.com/v3.1/funding-rounds/2792f36e8f1f45aabdf561cc7298c169"

response = requests.get(url,payload)   
raw_data = response.json()
json_data = raw_data['data']
property_data = json_data['properties']
relation_data = json_data['relationships']