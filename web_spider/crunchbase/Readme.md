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
*  


The Data Scrapping procedure is processed in the following way:

1. get the api requests
2. use corresponding data subsection deal with data frame
3. save the results





## Questions:

1. what is delete mean in the api document  

## Reference 

1. https://data.crunchbase.com/v3.1/reference