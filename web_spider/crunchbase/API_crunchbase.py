# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 11:52:34 2018

@author: xiaofeima

API data collecting for crunchbase
user_key=6c9ef18c935a0d984d463dd6bb872638
This saves scrapping procedure for different categories 

# organization info
# headquarter location
# funding round
# acquisition
# industry category


"""
import requests
import pandas as pd
import copy, time 
import json
import util
from table_format import*

## 

API_Prefix="https://api.crunchbase.com/v3.1"
User_key="2bddce7174abaf499d47ed2a4baf4581"


class API_source:
    def __init__(self,api_section,user_key=User_key):
        self.api_url = API_Prefix+api_section
        self.user_key = user_key
        self.api_section = api_section
    
    ## summary part 
    def api_organization_collect_summary(self,query_para,flag_status):
        '''
        get summarized info of ipo from crunchbase 
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            page_info
                indicating the page information we need in the next run
            df_temp
                dataframe we collect 
        '''
        # get the raw data 
        # start_url = self.api_prefix + API_ENDPOINT['ipo']
        query_para["user_key"] = User_key
        key_word = "properties"
        flag,raw_json = util.get_raw_data(self.api_url,query_para)
        if flag == 0:
            return 0,"",""
        else:
            page_info, data_info = util.meta_info(raw_json,flag_status)

            df_temp = pd.DataFrame(data_info)
            df_temp = pd.concat([df_temp.drop([key_word],axis=1),df_temp[key_word].apply(pd.Series)],axis=1)
            df_temp = df_temp[organization_summary_col]
        if page_info["next_page_url"]:
            self.api_url = page_info["next_page_url"]

        return 1,page_info,df_temp


    def api_ipo_collect_summary(self,query_para,flag_status):
        '''
        get summarized info of ipo from crunchbase 
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            page_info
                indicating the page information we need in the next run
            df_temp
                dataframe we collect 
        '''
        # get the raw data 
        # start_url = self.api_prefix + API_ENDPOINT['ipo']
        query_para["user_key"] = User_key
        key_word = "properties"
        flag,raw_json = util.get_raw_data(self.api_url,query_para)
        if flag == 0:
            return 0,"",""
        else:
            page_info, data_info = util.meta_info(raw_json,flag_status)

            df_temp = pd.DataFrame(data_info)
            df_temp = pd.concat([df_temp.drop([key_word],axis=1),df_temp[key_word].apply(pd.Series)],axis=1)
            df_temp = df_temp[IPO_summary_col]
        if page_info["next_page_url"]:
            self.api_url = page_info["next_page_url"]

        return 1,page_info,df_temp

    def api_people_summary(self,query_para,flag_status):
        '''
        get summarized info of people from crunchbase 
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0-> fail 1-> success
            page_info
                indicating the page information we need in the next run
            df_temp
                dataframe we collect 
        '''
        # get the raw data 
        # start_url = self.api_prefix + API_ENDPOINT['ipo']
        query_para["user_key"] = User_key
        key_word = "properties"
        flag,raw_json = util.get_raw_data(self.api_url,query_para)
        if flag == 0:
            return 0,"",""
        else:
            page_info, data_info = util.meta_info(raw_json,flag_status)

            df_temp = pd.DataFrame(data_info)
            df_temp = pd.concat([df_temp.drop([key_word],axis=1),df_temp[key_word].apply(pd.Series)],axis=1)
            df_temp = df_temp[people_summary_col]
        if page_info["next_page_url"]:
            self.api_url = page_info["next_page_url"]

        return 1,page_info,df_temp





    ## detailed info
    def api_organization_detail(self,query_UUID,query_key=User_key):
        '''
        get info from crunchbase
        input argument:
            query_UUID:
                The permalink of the organization or the UUID of the organization
            query_key: 
                provide the user key
        return variables:
            flag
                indicating the current process 0->fail 1->success
            df_property
                information about organization  

        '''
        ### get the raw data 
        payload = {'user_key': query_key}
        flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
        if flag == 0:
            return 0,"",""
        else:
            property_info,relationship = util.detail_info(raw_json)
            key_word = "properties"
            df_property = pd.DataFrame(property_info)
            df_property = df_property[organization_property_col1]
            df_temp = pd.concat([df_temp.drop([key_word],axis=1),df_temp[key_word].apply(pd.Series)],axis=1)
            df_temp = df_temp[organization_property_col1]
            df_relation = pd.DataFrame(relationship)

            ### founding round 
            if relationship['funding_rounds']['paging']['total_items'] > 0:
                df_property['num_founding_round'] = int(relationship['funding_rounds']['paging']['total_items'])
            
            funding_info = relationship['funding_rounds']['items']
            df_property['current_funding_type'] = funding_info['funding_type']
            df_property['current_funding_series'] = funding_info['series']

            ### operating status
            if relationship['acquired_by']['paging']['total_items'] == 0 and df_property['closed_on']:
                df_property['status'] = "operating"
            elif relationship['acquired_by']['paging']['total_items'] > 0:
                df_property['status'] = "acquired"
            if df_property['closed_on'] == False:
                df_property['status'] = "closed"

            ### category
            if relationship['categories']['paging']['total_items'] > 0 :
                category_list= relationship['categories']['items']
                cat_info_list=[]
                cat_groups_list=[]
                for ele in category_list:
                    cat_info_list.append(ele['properties']['name'])
                    cat_groups_list.append(ele['properties']['category_groups'])
        
                



            return 1,df_property


    def api_degree_jobs_detail(self,query_UUID,query_key=User_key):
        '''
        get info of people from crunchbase
            people degree info
            people jobs info
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            flag
                indicating the current process 0->fail 1->success
            df_property
                information about organization  
        '''
        # get the raw data 
        payload = {'user_key': query_key}
        flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
        if flag == 0:
            return 0,"",""
        else:
            property_info,relation_ship = util.detail_info(raw_json)
            df_property = pd.DataFrame(property_info)
            df_relation = pd.DataFrame(relation_ship)


            ## people extra
            people_dict = {
                 'uuid':query_UUID,
                 'born_on':df_property['born_on'],
                 'rank':df_property['rank'],
             }
            people_df = pd.DataFrame(people_dict)

            ## degree
            degree_df_temp  = {
                    'people_id': "",
                    ## school info
                    'degree_type': "",
                    'subject': "",
                    'institution': "",
                    'graduated_at': "",
                    'started_at': "",
                }
            degree_df_temp_list=[]
            degree_list = df_relation['degrees']['items']
            if len(degree_list) > 0:
                for ele in degree_list:
                    degree_df_temp['people_id'] = query_UUID
                    
                    for key1, key2 in degree_dict.items():
                        degree_df_temp[key1] = ele[key2]
                    
                    ## institution
                    temp_relation = ele['relationships']['school']['properties']
                    degree_df_temp['institution'] = temp_relation['name']
                    degree_df_temp_list.append(degree_df_temp)
                degree_df = pd.DataFrame(degree_df_temp_list)

            ## jobs
            jobs_df_temp_list=[]
            jobs_list = df_relation['jobs']['items']
            if len(jobs_list) > 0:
                for ele in jobs_list:
                    jobs_df_temp = {}
                    jobs_df_temp['people_id'] = query_UUID
                    jobs_df_temp['title'] = ele['properties']['title']
                    jobs_df_temp['started_on'] = ele['properties']['started_on']
                    jobs_df_temp['ended_on'] = ele['properties']['ended_on']
                    jobs_df_temp['is_current'] = ele['properties']['is_current']
                    jobs_df_temp['job_type'] = ele['properties']['job_type']
                    jobs_df_temp['affiliation'] = ele['relationships']['name']

                    jobs_df_temp_list = jobs_df_temp
                jobs_df = pd.DataFrame(jobs_df_temp_list)

        return 1, people_df, degree_df, jobs_df


    def api_fundinground_detail(self,query_UUID,query_key=User_key):
        '''
        get info from crunchbase
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            df_property
                information about organization  
        '''
        # get the raw data 
        payload = {'user_key': query_key}
        flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
        if flag == 0:
            return 0,"",""
        else:
            property_info,relation_ship = util.detail_info(raw_json)

            df_property = pd.DataFrame(property_info)
            df_relation = pd.DataFrame(relation_ship)
            
            # add the relationship (people) connect to people part use uuid

        return 1,df_property,df_relation

    def api_acquisition_detail(self,query_UUID,query_key=User_key):
        '''
        get info from crunchbase
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            df_property
                information about organization  
        '''
        # get the raw data 
        payload = {'user_key': query_key}
        flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
        if flag == 0:
            return 0,"",""
        else:
            property_info,relation_ship = util.detail_info(raw_json)

            df_property = pd.DataFrame(property_info)
            df_relation = pd.DataFrame(relation_ship)
            
            # add the relationship (people) connect to people part use uuid

        return 1,df_property,df_relation

    def api_ipo_detail(self,query_para,flag_status):
        '''
        get info from crunchbase
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            df_property
                information about organization  
        '''
        # get the raw data 
        payload = {'user_key': query_key}
        flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
        if flag == 0:
            return 0,"",""
        else:
            property_info,relation_ship = util.detail_info(raw_json)

            df_property = pd.DataFrame(property_info)
            df_relation = pd.DataFrame(relation_ship)
            
            # add the relationship (people) connect to people part use uuid

        return 1,df_property,df_relation

    def api_fund_detail(self,query_para,flag_status):
        '''
        get info from crunchbase
        input argument:
            query_para: 
                updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
                sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
                page: Page number of the results to retrieve.
        return variables:
            flag
                indicating the current process 0->fail 1->success
            df_property
                information about organization  
        '''
        # get the raw data 
        payload = {'user_key': query_key}
        flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
        if flag == 0:
            return 0,"",""
        else:
            property_info,relation_ship = util.detail_info(raw_json)

            df_property = pd.DataFrame(property_info)
            df_relation = pd.DataFrame(relation_ship)
            
            # add the relationship (people) connect to people part use uuid

        return 1,df_property,df_relation

