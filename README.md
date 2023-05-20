# Windmill


Data processing pipeline that ingests raw data and:

●	Cleans the data: The raw data contains missing values and outliers, which must be removed or imputed.

●	Calculates summary statistics: For each turbine, calculate the minimum, maximum, and average power output over a given time period (e.g., 24 hours).

●	Identifies anomalies: Identify any turbines that have significantly deviated from their expected power output over the same time period. Anomalies can be defined as turbines whose output is outside of 2 standard deviations from the mean.

●	Stores the processed data: Store the cleaned data and summary statistics in a database for further analysis.


Data is provided as multiple csv files. 

## Assumptions 

1. .csv files are to be stored in a provided path, this resource should be accessible to the script/docker.
2. path to the .csv files can be set via environment variables and volume can be mounted via the dockerfile.
I'll just copy the datafiles in the dockerfile build for simplicity here.
3. no other system is dependent on these csv dumps so they may be erased after each interrogation. I've implemented a
flag, (can also be set via environment variable) that will delete the files after computing the summary statistics.
4. Ideally we should have another table with turbines and the turbine_id should be a foreignkey to that table.
5. I've assumed that anomaly detection (power output drops) are to be calculated for each turbine individually.
6. I've assumed that the data format (columns of interest and their datatypes) will remain the same.
7. I've worked without the assumption that a particular turbine will always be in the same .csv file but
I've assumed that all data for a particular turbine will be in the same .csv file. 
8. Not necessarily an assumption, more a mention, the .env file is pushed to the repo, this is not a good practice
but i've done it for simplicity. In a real world scenario, the .env file should be gitignored.

## Design and implementation

The design involves using a flask app as  minimal interface with the script. Upon starting the service,
the script will be run and the results will be stored in a postgresql database. The user can trigger the data
fetching by an API call and he can retrieve the anomalies by another API call.

Main entrypoint is fetch_data, files will be fetched from the provided path and stored in a pandas dataframe.
The dataframe is then cleaned and summary statistics are calculated. The results are stored in a postgresql database.

### Features

1. a particular turbine doesn't necessarily need to be in the same csv file
2. should the data be incomplete and the .csv batches contain different amounts of data, the script will not break.
We are calculating on each iteration how many 24hr (in this case) batches there are to compute.
3. The 24hr time window is configurable in seconds via the .env file.
4. User can set to keep the imported datapoints and files via 2 different .env config variables.

### Future improvements (among others)

1. db relationships can be improved.
2. A scheduler task can run in the background and fetch data at a given interval. Was initially implemented but
needed some debugging so i dropped it. 
3. Some more endpoints for data retrieval can be added (anomalies by turbine id or by time window)
4. Testing can be improved, i've only added one test and the create_app is just duplicated code from the main.
5. Flask app can be served via gunicorn or uwsgi.
6. Dockerfile can be improved to mount a volume for the datafiles and exclude tests folder from the image.
7. Not all git commits have titles and are not that well structured, i've revisited the logic several times
during the implementation.
8. I would have liked to implement a lock mechanism for the datafiles, so that if the script is running and
a user tries to fetch anomalies or data, he will be notified that the script is running and he should try again later.


## Installation

Clone the repo and use `docker-compose up` to start the services. The flask app will be available on port `5007` and
the database can be interrogated on port `8888`.
