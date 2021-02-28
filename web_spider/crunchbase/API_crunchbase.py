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
    def api_organization_summary(self,query_para,flag_status):
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


    def api_ipo_summary(self,query_para,flag_status):
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

    def api_funding_round_summary(self,query_para,flag_status):
        '''
        get summarized info of funding from crunchbase 
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
            df_temp = df_temp[funding_round_summary_col]

            if page_info["next_page_url"]:
                self.api_url = page_info["next_page_url"]

            return 1,page_info,df_temp       

    def api_acquisition_summary(self,query_para,flag_status):
        '''
        get summarized info of acquisition from crunchbase 
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
            df_temp = df_temp[acquisition_summary_col]

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
            property_info,relation_ship = util.detail_info(raw_json)
            key_word = "properties"
            df_property = pd.DataFrame(property_info)
            df_property = df_property[organization_property_col1]
            df_temp = pd.concat([df_temp.drop([key_word],axis=1),df_temp[key_word].apply(pd.Series)],axis=1)
            df_temp = df_temp[organization_property_col1]
            df_relation = pd.DataFrame(relation_ship)

            ### founding round 
            if relation_ship['funding_rounds']['paging']['total_items'] > 0:
                df_property['num_founding_round'] = int(relation_ship['funding_rounds']['paging']['total_items'])
            
            funding_info = relation_ship['funding_rounds']['items']
            df_property['current_funding_type'] = funding_info['funding_type']
            df_property['current_funding_series'] = funding_info['series']

            ### operating status
            if relation_ship['acquired_by']['paging']['total_items'] == 0 and df_property['closed_on']:
                df_property['status'] = "operating"
            elif relation_ship['acquired_by']['paging']['total_items'] > 0:
                df_property['status'] = "acquired"
            if df_property['closed_on'] == False:
                df_property['status'] = "closed"

            ### category
            if relation_ship['categories']['paging']['total_items'] > 0 :
                category_list= relation_ship['categories']['items']
                cat_info_list=[]
                cat_groups_list=[]
                for ele in category_list:
                    cat_info_list.append(ele['properties']['name'])
                    cat_groups_list.append(ele['properties']['category_groups'])
        

            return 1,df_property

    ## degree job detail
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

            ## people extra
            people_dict = {
                 'uuid':query_UUID,
                 'born_on':property_info['born_on'],
                 'rank':property_info['rank'],
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
            degree_list = relation_ship['degrees']['items']
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
            jobs_list = relation_ship['jobs']['items']
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

    ## funding investment detail
    def api_investment_detail(self,query_UUID,query_key=User_key):
        '''
        get info of funding round and investment from crunchbase
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
            items_info = util.relation_info(raw_json)
            investment_data_list=[]
            for ele_item in items_info:
                investment_temp = {}
                property_info = ele_item['properties']
                relationship_info = ele_item['relationships']
            
                ## investment part 
                investment_dict = {
                    'funding_round_id':  query_UUID,
                    'investment_id':  ele_item['uuid'],  
                    'money_invested': property_info['money_invested'],
                    'money_invested_currency_code': property_info['money_invested_currency_code'],
                    'money_invested_usd': property_info['money_invested_usd'],
                    'is_lead_investor': property_info['is_lead_investor'],
                    'announced_on': property_info['announced_on'],
                    }
                
                
                ## related person and funded organization
                investor_info = relationship_info["investors"]
                investor_property = investor_info['properties']
                investor_dict = {
                    "investor_id": investor_info['uuid'],
                    'investor_permalink': investor_info['permalink'],
                }
                firm_info = relationship_info['invested_in']
                funded_firm_dict ={
                    'target_id':firm_info['uuid'],
                    'target_permalink':firm_info['properties']['permalink']
                }

                investment_temp.update(investment_dict)
                investment_temp.update(investor_dict)
                investment_temp.update(funded_firm_dict)


                investment_data_list.append(investment_temp)
            
            df_investment = pd.DataFrame(investment_data_list)


            return 1,df_investment




    def api_acquisition_relation_detail(self,query_UUID,query_key=User_key):
        '''
        get acquisition info from crunchbase
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
            return 0,""
        else:
            property_info,relation_ship = util.detail_info(raw_json)


            acquisition_relation_data={}
            acquiree_data = relation_ship['acquiree']
            acquirer_data = relation_ship['acquirer']

            acquisition_dict = {
                'acquisition_id': query_UUID,

                'acquiree_id': acquiree_data['item']['uuid'],
                'acquiree_permalink': acquiree_data['item']['permalink'],

                'acquirer_id': acquirer_data['item']['uuid'],
                'acquirer_permalink': acquirer_data['item']['permalink'],
            }
 
            df_acquisition = pd.DataFrame(acquisition_dict)

            return 1,df_acquisition

    def api_ipo_funded_detail(self,query_UUID,query_key=User_key):
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
            return 0,""
        else:
            property_info,relation_ship = util.detail_info(raw_json)
            # add the relationship (people) connect to people part use uuid
            funded_company = relation_ship['item']
            IPO_funded_dict = {
                'ipo_id': query_UUID,
                'stock_exchange_symbol':property_info['stock_exchange_symbol'],
                'stock_symbol':property_info['stock_symbol'],
                'money_raised_usd':property_info['money_raised_usd'],
                'funded_company_id': funded_company['uuid'],
                'funded_company_permalink': funded_company['properties']['permalink'], 
            }

            df_IPO_funded=pd.DataFrame(IPO_funded_dict)


            return 1,df_IPO_funded


    # def api_fund_detail(self,query_para,flag_status):
    #     '''
    #     get info from crunchbase
    #     input argument:
    #         query_para: 
    #             updated_since: When provided, restricts the result set to Organizations where updated_at >= the passed value
    #             sort_order: The sort order of the collection. Options are "created_at ASC", "created_at DESC", "updated_at ASC", and "updated_at DESC"
    #             page: Page number of the results to retrieve.
    #     return variables:
    #         flag
    #             indicating the current process 0->fail 1->success
    #         df_property
    #             information about organization  
    #     '''
    #     # get the raw data 
    #     payload = {'user_key': query_key}
    #     flag,raw_json = util.get_raw_data(self.api_url+"/"+query_UUID, payload)
    #     if flag == 0:
    #         return 0,"",""
    #     else:
    #         property_info,relation_ship = util.detail_info(raw_json)

    #         df_property = pd.DataFrame(property_info)
    #         df_relation = pd.DataFrame(relation_ship)
            
    #         # add the relationship (people) connect to people part use uuid

    #         return 1,df_property,df_relation