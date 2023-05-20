from datetime import timedelta

from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from resources.models import *

load_dotenv()
session = db.session


# Generic functions
def db_insert_multiple_conflict(table, items, key='id'):
    """
    Insert multiple rows into a table, ignoring conflicts
    :param table:
    :param items:
    :param key:
    :return:
    """
    stmt = insert(table).values(items)
    stmt = stmt.on_conflict_do_nothing(index_elements=[key])
    try:
        session.execute(stmt)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e


# DataLog
def db_get_turbine_datalog_last_entry(turbine_id):
    # Get last entry by timestamp
    return session.query(DataLog).filter_by(turbine_id=turbine_id).order_by(DataLog.job_timestamp.desc()).first()


def db_insert_datalog(item):
    log = DataLog(**item)
    session.add(log)
    try:
        session.commit()
        return log
    except SQLAlchemyError as e:
        session.rollback()
        raise e


# TurbineData
def db_get_turbine_first_entry(turbine_id):
    # Get last entry by timestamp
    return session.query(TurbineData).filter_by(turbine_id=turbine_id).order_by(TurbineData.timestamp.asc()).first()


def db_get_turbine_data_interval(turbine_id, timestamp, compute_time_window):
    # Calculate the timestamp range using timedelta
    start_timestamp = timestamp - timedelta(seconds=compute_time_window)

    # Get the data within the timestamp range and for the specific turbine_id
    return session.query(TurbineData).filter(
        TurbineData.turbine_id == turbine_id,
        TurbineData.timestamp.between(start_timestamp, timestamp)
    ).all()


def db_insert_turbine_data(items):
    # Insert rows into database
    db_insert_multiple_conflict(TurbineData, items)


def db_wipe_turbine_data(turbine_id, timestamp):
    # Delete all rows within the timestamp range and for the specific turbine_id
    session.query(TurbineData).filter(
        TurbineData.turbine_id == turbine_id,
        TurbineData.timestamp <= timestamp
    ).delete()
    session.commit()


# ComputedData
def db_get_computed_data(turbine_id):
    # Get last entry by timestamp
    return session.query(ComputedData).filter_by(turbine_id=turbine_id)\
        .order_by(ComputedData.timestamp.desc()).all()


def db_get_computed_last_entry(turbine_id):
    # Get last entry by timestamp
    return session.query(ComputedData).filter_by(turbine_id=turbine_id)\
        .order_by(ComputedData.timestamp.desc()).first()


def db_insert_computed_data(item):
    # Insert rows into database
    data = ComputedData(**item)
    session.add(data)
    try:
        session.commit()
        return data
    except SQLAlchemyError as e:
        session.rollback()
        raise e


# Anomaly
def db_get_anomalies():
    # Get all anomalies
    return session.query(Anomaly).all()


def db_insert_anomalies(items):
    # Insert rows into database
    db_insert_multiple_conflict(Anomaly, items)







