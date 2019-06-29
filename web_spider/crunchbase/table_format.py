# this files saves table format for the database
'''

mimics the snapshot to create the database


Organization: 
id
first_funding
last_funding 
founding_round
status
category
founded at 

people
id
afflictions
related organization
job position

degree
id
degree_type
subject
institution
graduated_at



jobs
id
people_id
organization_id
title
is_current
started_on
ended_on


funds:
fund_id 
organization_id 
funding_name

funding_rounds (detailed info)
normal 

acquisitions 
acquiring_organization_id
acquired_organization_id
funding_amount
acquired date
'''
### Summary part 
# organization
# people
# funding round 
# acquisition
# ipo
# category


organization_summary_col=[
    'uuid',
    'permalink',
    'name',
    'primary_role',
    'stock_exchange',
    'stock_symbol',
    'homepage_url',

    'city_name',
    'region_name',
    'country_code',
]


people_summary_col = [
    'uuid'
    'permalink',
    'web_path',
    'first_name',
    'last_name',
    'gender',
    'role_investor',
    'organization_name',
    'title',
    'city_name',
    'region_name',
    'country_code',
]


##IPO
IPO_summary_col = [
    'uuid',
    # property
    'went_public_on',
    'went_public_on_trust_code',
    'stock_exchange_symbol',
    'stock_symbol',
    'shares_sold',
    'money_raised',
    'money_raised_currency_code',
    'money_raised_usd',
]


## funding info 
funding_round_summary_col=[
    'uuid',
    'funding_type',
    'series',
    'series_qualifier',
    'announced_on',
    'closed_on',
    'money_raised',
    'money_raised_currency_code',
    'money_raised_usd',

    'target_money_raised',
    'target_money_raised_currency_code',
    'target_money_raised_usd',
    
    'pre_money_valuation',
    'pre_money_valuation_currency_code',
    'pre_money_valuation_usd',
    'rank',    

]

acquisition_summary_col = [
    'uuid',
    'price',
    'price_currency_code',
    'price_usd',
    'payment_type',
    'acquisition_type',
    'acquisition_status',
    'disposition_of_acquired',
    'announced_on',
    'rank',

]


### people extra
people_extra_col = [
    'born_on',
    'rank',

]

### degree 
degree_col = [
    'people_id',
    ## school info
    'degree_type',
    'subject',
    'institution',
    'graduated_at',
    'started_at',
]

degree_dict = {
    ## school info
    'degree_type': 'degree_type_name',
    'subject': 'degree_subject',
    'graduated_at':'completed_on',
    'started_at':'started_on',
}

### jobs
job_col = [
    'people_id',
    'organization_id',
    'affiliation',
    'title',
    'is_current',
    'started_on',
    'ended_on',
    ]

job_dict = {
    'organization_id':'uuid',
    'affiliation':'name',
    'title':'title',
    'job_type':'job_type',
    'is_current':'is_current',
    'started_on':"started_on",
    'ended_on':"ended_on",
    }

## detail

organization_property_col1=[
    'permalink',
    'name',
    'short_description',
    'primary_role',
    'role_company',
    'role_investor',
    'role_group',
    'role_school',
    'investor_type',
    'founded_on',
    'is_closed',
    'closed_on',
    'num_employees_min',
    'num_employees_max',
    'stock_exchange',
    'stock_symbol',
    'total_funding_usd',
    'number_of_investments',
    'homepage_url',
    'phone_number',
    'rank',
    'created_at',
    'updated_at']
organization_property_col2=[
    'status',
    'num_founding_round',
    'current_funding_type',
    'current_series',
    'category_code',
    'category_group',
]


investment_col= [
    'funding_round_id'
    'investment_id',
    'money_invested',
    'money_invested_currency_code',
    'money_invested_usd',
    'is_lead_investor',
    'announced_on',
    'investor_id',
    'investor_permalink',
    'target_id',
    'target_permalink'


]