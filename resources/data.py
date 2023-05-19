from dotenv import load_dotenv
from loguru import logger
import os
import pandas as pd

from resources.db import db_get_turbine_last_entry, db_insert_turbine_data, db_insert_datalog

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")


def fetch_data():
    # Get all .csv files in DATA_PATH
    files = [x for x in os.listdir(DATA_PATH) if x.endswith(".csv")]
    logger.info(f"Found {len(files)} files in {DATA_PATH}")
    for f in files:
        logger.debug(f"Processing {f}")
        df = pd.read_csv(os.path.join(DATA_PATH, f))
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        logger.debug(f"Found {len(df)} rows")
        # Group rows by turbine_id
        for turbine_id, group in df.groupby("turbine_id"):
            logger.debug(f"Processing turbine {turbine_id}")
            last_entry = db_get_turbine_last_entry(turbine_id)
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

    logger.info("Recurring task executed")

    return {"success": True}


