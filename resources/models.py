import datetime
from dataclasses import dataclass
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Float, String, DateTime, Integer, Boolean, ARRAY, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, registry, relationship

db = SQLAlchemy()


@dataclass
class TurbineData(db.Model):
    __tablename__ = 'turbine_data'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    turbine_id: Mapped[int] = mapped_column(Integer)
    wind_speed: Mapped[float] = mapped_column(Float)
    wind_direction: Mapped[int] = mapped_column(Integer)
    power_output: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


@dataclass
class DataLog(db.Model):
    __tablename__ = 'job_logs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    turbine_id: Mapped[int] = mapped_column(Integer)
    job_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    last_entry: Mapped[datetime.datetime] = mapped_column(DateTime)


@dataclass
class ComputedData(db.Model):
    __tablename__ = 'computed_data'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    turbine_id: Mapped[int] = mapped_column(Integer)
    compute_time_window: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    min: Mapped[float] = mapped_column(Float)
    max: Mapped[float] = mapped_column(Float)
    average: Mapped[float] = mapped_column(Float)

    anomalies: Mapped[Optional[List["Anomaly"]]] = relationship(back_populates="computed_data", lazy=None)

@dataclass
class Anomaly(db.Model):
    __tablename__ = 'anomalies'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    output_deviation: Mapped[float] = mapped_column(Float)
    anomaly_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)

    computed_data_id: Mapped[int] = mapped_column(ForeignKey('computed_data.id'))
    computed_data: Mapped[Optional["ComputedData"]] = relationship(back_populates="anomalies", lazy=None)
