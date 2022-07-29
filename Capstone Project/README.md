# Capstone Project

# Project Summary
In this project I have created a Redshift datawarehouse containing immigration and demography data which was stored in a S3 buckets on AWS.

I took the steps as follows; (1) define the scope of the project and gather the relevant data, (2) conduct exploratory analysis, (3) define the data model, (4) run ETL pipelines to model the data, (5) write up a summary of this project.


# 1. Scope
For this data, I will use immigration data, world temperature data and US demographic data to setup a data warehouse with fact and dimension tables.
This project will integrate I94 immigration data, world temperature data and US demographic data to setup a data warehouse with fact and dimension tables.

Data Sets can be found here; 
    1. [I94 Immigration Data](https://travel.trade.gov/research/reports/i94/historical/2016.html)
    2. [World Temperature Data](https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data)
    3. [U.S. City Demographic Data](https://public.opendatasoft.com/explore/dataset/us-cities-demographics/export/)


# 2 Explore data

I used pandas to translate source data into a dataframe so that it can easily be interrogated. I then cleaned the data as appropriate so that I could better define my data model. Please see capstone_project.ipynb for the details.


# 3 Data Modelling 
I used the star schema to model the fact and dimension tables given that the predominant use-case will be for querying on Power BI.

# 4 Data pipelines
In this step I gathered data from the relevant S3 buckets, cleaned the data as per step 2, transformed this data into fact and dimension tables, and finally stored these tables back into the target S3 bucket. Data processing and data model was created by Spark.

I added data quality checks for empty tables after running the ETL data pipeline as well as mactching rules between the data schema of every dim table and data model.


# 5 Summary
The main tools I used were AWS S3 for data storage, Pandas for exploratory data analysis, Spark for ldata data set processing to transform staging tables to dimensional tables. I created immigration and temperature data sets and ran an ETL pipeline that transformed raw data into useful OLAP cubes to be queries by users.
