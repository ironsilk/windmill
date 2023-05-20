import os
from datetime import timedelta

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from resources.db import db_get_turbine_datalog_last_entry, db_insert_turbine_data, db_insert_datalog, \
    db_get_turbine_data_interval, db_insert_computed_data, db_insert_anomalies, db_get_computed_last_entry, \
    db_get_turbine_first_entry, db_wipe_turbine_data

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
COMPUTE_INTERVAL = int(os.getenv("COMPUTE_INTERVAL", 86400))
WIPE_DATA = os.getenv("WIPE_DATA")
if WIPE_DATA is not None:
    WIPE_DATA = WIPE_DATA.lower() == "true"
WIPE_FILES = os.getenv("WIPE_FILES")
if WIPE_FILES is not None:
    WIPE_FILES = WIPE_FILES.lower() == "true"

# pandas print all columns
pd.set_option('display.max_columns', None)


def preprocess_data(df):
    """
    Preprocesses the data by converting the timestamp to datetime, removing rows with missing values, and removing outliers.

    :param df: The input DataFrame to be preprocessed.
    :return: The preprocessed DataFrame.
    """
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Remove rows with missing values
    df = df.dropna()

    # Remove outliers
    # TODO this needs further discussion on what outliers actually means
    #  and how to handle them. For now, we just remove rows with
    #  wind_speed > 25 or wind_speed < 0.
    #  df.describe() does not show any significant outliers, at least from a quick glance.
    #  If this needs to be computed while taking into consideration historical data, then maybe
    #  we should move this down the pipeline.
    df = df[df["wind_speed"] < 25]
    df = df[df["wind_speed"] > 0]
    df = df[df["wind_direction"] < 360]

    return df


def compute_batch_stats(turbine_id, current_timestamp):
    """
    Compute statitics for 24hrs prior to the current_timestamp
    :param turbine_id:
    :param current_timestamp:
    :return:
    """
    data = db_get_turbine_data_interval(turbine_id, current_timestamp, COMPUTE_INTERVAL)
    df = pd.DataFrame([x.__dict__ for x in data])
    return df, {
        "turbine_id": turbine_id,
        "min": df["power_output"].min(),
        "max": df["power_output"].max(),
        "average": df["power_output"].mean(),
        "timestamp": current_timestamp,
        "compute_time_window": COMPUTE_INTERVAL,
    }


def compute_anomalies(df, batch_id):
    """
    Compute anomalies for a given batch
    :param df:
    :param batch_id:
    :return:
    """
    df['computed_data_id'] = batch_id
    df.rename(columns={'timestamp': 'anomaly_timestamp'}, inplace=True)
    mean_power = df['power_output'].mean()
    std_power = df['power_output'].std()
    df['output_deviation'] = df['power_output'] - mean_power
    df['anomaly'] = df['power_output'].apply(lambda x: 1 if x > mean_power + 2 * std_power or x < mean_power - 2 * std_power else 0)
    anomalies = df.loc[df['anomaly'] == 1]

    if not anomalies.empty:
        return anomalies[['output_deviation', 'anomaly_timestamp', 'computed_data_id']].to_dict('records')

    return []


def compute_data(turbine_id, new_last_entry):
    """
    Compute data and anomalies for a given turbine ID and new last entry.

    :param turbine_id: ID of the turbine to compute data for
    :param new_last_entry: New last entry for the turbine
    :param wipe_data: Flag indicating whether to wipe the data after computation (default: WIPE_DATA)
    """
    # Get last entry by timestamp
    last_entry = db_get_computed_last_entry(turbine_id)
    if not last_entry:
        # Means there's no computed data for this turbine, get first available datapoint
        last_entry = db_get_turbine_first_entry(turbine_id)
    # Check if last computed data is 24hrs older than last entry
    if last_entry and (new_last_entry - last_entry.timestamp).total_seconds() < COMPUTE_INTERVAL:
        logger.debug(f"Skipping computation for turbine {turbine_id}")
        return
    else:
        # Compute averages for 24hrs batches since last computed data
        current_timestamp = last_entry.timestamp + timedelta(hours=24) if last_entry else new_last_entry
        while current_timestamp <= new_last_entry:
            df, stats = compute_batch_stats(turbine_id, current_timestamp)
            inserted = db_insert_computed_data(stats)
            current_timestamp += timedelta(hours=24)
            yield df, inserted.id


def compute_data_and_anomalies(turbine_id, new_last_entry, wipe_data=WIPE_DATA):
    """
    Compute data and anomalies for a given turbine ID.

    :param turbine_id: ID of the turbine to compute data for.
    :param new_last_entry: New last entry for the turbine.
    :param wipe_data: Flag indicating whether to wipe the data after computation (default: WIPE_DATA).
    """

    computed_batch_dfs = compute_data(turbine_id, new_last_entry)
    for batch_df, batch_id in computed_batch_dfs:
        anomalies = compute_anomalies(batch_df, batch_id)
        if len(anomalies) > 0:
            logger.debug(f"Found {len(anomalies)} anomalies")
            db_insert_anomalies(anomalies)

    # Additionally we can also wipe the data after the computed data has been saved
    if wipe_data:
        db_wipe_turbine_data(turbine_id, new_last_entry)


def fetch_data():
    """
    Fetches data from .csv files in the specified path, preprocesses the data, and inserts it into the database.

    :return: A dictionary indicating the success of the fetch operation.
    """

    # Get all .csv files in DATA_PATH
    files = [x for x in os.listdir(DATA_PATH) if x.endswith(".csv")]
    logger.info(f"Found {len(files)} files in {DATA_PATH}")
    for f in files:
        logger.debug(f"Processing {f}")
        df = pd.read_csv(os.path.join(DATA_PATH, f))

        # Preprocess data
        df = preprocess_data(df)

        logger.debug(f"Found {len(df)} rows")
        # Group rows by turbine_id
        for turbine_id, group in df.groupby("turbine_id"):
            logger.debug(f"Processing turbine {turbine_id}")
            last_entry = db_get_turbine_datalog_last_entry(turbine_id)
            # Filter out rows that are already in the database
            if last_entry:
                group = group[group.timestamp > last_entry.last_entry]

            # Insert rows into database
            if len(group) > 0:
                db_insert_turbine_data(group.to_dict(orient="records"))
                # Update DataLog table
                db_insert_datalog({
                    "turbine_id": turbine_id,
                    "last_entry": group.timestamp.max(),
                })
                logger.debug(f"Inserted {len(group)} rows into database")

                # Compute statistics
                compute_data_and_anomalies(turbine_id, group.timestamp.max())
        # Wipe files after processing
        if WIPE_FILES:
            os.remove(os.path.join(DATA_PATH, f))

    logger.info("Recurring task executed")

    return {"success": True}



