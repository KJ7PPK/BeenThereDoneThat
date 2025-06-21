from sqlalchemy import (
    Table, Column, Integer, String, DateTime, Float, JSON, MetaData
)
from sqlalchemy.sql import func

metadata = MetaData()

transportations = Table(
    "transportations", metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(20), nullable=False),        # "plane","hotel","cruise","drive","train","visited"
    Column("name", String(200), nullable=False),
    Column("description", String, nullable=True),
    Column("date", DateTime, nullable=True),
    Column("end_date", DateTime, nullable=True),       # for cruises/hotels
    Column("origin_latitude", Float, nullable=True),
    Column("origin_longitude", Float, nullable=True),
    Column("destination_latitude", Float, nullable=True),
    Column("destination_longitude", Float, nullable=True),
    Column("extra", JSON, nullable=True),              # e.g. {"distance":200,"nights":3,...}
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)
