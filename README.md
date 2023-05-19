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
3. no other system is dependent on these csv dumps so they may be erased after each interrogation
4. If assumption (2) is not true we can implement a last_timestamp or such flag that will continue with 
provided data from that point forward. Implemented the model.
5. Ideally we should have another table with turbines and the turbine_id should be a foreignkey to that table.
6. 