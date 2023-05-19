import os
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from resources.models import *

load_dotenv()
session = db.session


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


def db_get_turbine_last_entry(turbine_id):
    # Get last entry by timestamp
    return session.query(DataLog).filter_by(turbine_id=turbine_id).order_by(DataLog.job_timestamp.desc()).first()


def db_insert_turbine_data(items):
    # Insert rows into database
    db_insert_multiple_conflict(TurbineData, items)


def db_insert_datalog(item):
    log = DataLog(**item)
    session.add(log)
    try:
        session.commit()
        return log
    except SQLAlchemyError as e:
        session.rollback()
        raise e







