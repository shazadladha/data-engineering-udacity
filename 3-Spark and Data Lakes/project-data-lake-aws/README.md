# Project summary

In this project, I built an ETL pipeline for a data lake using Spark. The tables createdused data from two S3 sources:

# running the project
You can run this project via the CLI: `python3 etl.py`.

# etl.py
There are two main functions in `etl.py`, namley, `process_song_data()` and `process_log_data()`. These functions perform operations that were done with SQL queries in previous exercises