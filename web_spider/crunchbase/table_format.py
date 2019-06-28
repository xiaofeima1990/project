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

## organization part
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

## people part
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



IPO_summary_col = [
    'uuid',
    # property
    'api_url',
    'went_public_on',
    'went_public_on_trust_code',
    'stock_exchange_symbol',
    'stock_symbol',
    'shares_sold',
    'money_raised',
    'money_raised_currency_code',
    'money_raised_usd',
]


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

## funding info 


