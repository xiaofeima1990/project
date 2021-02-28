# Readme
This mini Crunchbase data collection project aims to collect VC data from the crunchbase for research purpose.
The database consist of: 

* organization_summary
* organization_detail
* people_summary
* people_detail
* categories
* locations
* funding-rounds_summary
* funding-rounds_detail
* acquistion_summary
* acquisition_detail
* ipo_summary
* ipo_detail
* fund_summary
* fund_detail


Code Structure:

* main.py: in charge of main data collection
* util.py: get the data, build the link with database, write and read data
* API_crunchbase.py: get access to each data section, and clean the raw data for saving 



The Data Scrapping procedure is processed in the following way:

1. get the api requests
2. use corresponding data subsection deal with data frame
3. save the results


Database Structure: 
tables: 
* company 
* investor
* school
* investment
* funding_round
* fund
* ipo
* acquisition 
* people
* jobs
* degree 



**company** 

uuid,entity_type,name, permalink, category_code, status, founded_at, closed_at, web_domain,short_description,rank,
country_code, state_code, city, region, 
num_founding_rounds,funding_total_usd,FundingRound_group,first_funding_at, last_funding_at, 
relation_founder, 
acquisition_uuid,acquired_name, acquired_uuid,ipo_uuid,stock_code, 
num_employees_min, num_employees_max, 
primary_role, role_company,role_investor,role_group,role_school

**investor**

uuid,entity_type,name,permalink,investor_type, founded_at, closed_at, web_domain,short_description,rank
country_code, state_code, city, region,
num_investment,
relation_founder,
num_employees_min, num_employees_max, 
primary_role, role_company,role_investor,role_group,role_school

**school**

uuid,entity_type,name,normalized_name, permalink,investor_type, founded_at, closed_at, web_domain,short_description,rank,
country_code, state_code, city, region, 
num_founding_rounds,FundingRound_group
relation_founder, 
primary_role, role_company,role_investor,role_group,role_school

**funding round**
uuid,funding_type,series,series_qualifier,rank
announced_on,closed_on,

money_raised,money_raised_currency_code,money_raised_usd
target_money_raised,target_money_raised_currency_code,target_money_raised_usd,
pre_money_valuation,pre_money_valuation_currency_code,pre_money_valuation_usd

**IPO**
uuid,
went_public_on,went_public_on_trust_code,stock_exchange_symbol,
stock_symbol,shares_sold
money_raised,money_raised_currency_code,money_raised_usd

**acquisition**
uuid,announced_on,rank
price,price_currency_code,price_usd,payment_type
acquisition_type,acquisition_status,disposition_of_acquired

**people**
uuid,permalink,web_path,first_name,last_name,gender
role_investor,organization_name,title
city_name,region_name,country_code





## Questions:

1. what is delete mean in the api document  

## Reference 

1. https://data.crunchbase.com/v3.1/reference