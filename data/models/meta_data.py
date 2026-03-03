from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from database.db import DatabaseConnector


class Base(DeclarativeBase):
    pass


# Base.metadata.create_all(DatabaseConnector.get_engine())
