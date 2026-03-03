import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

HOST_DB_TEST = os.environ.get("HOST_DB_TEST")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
DATABASE_URL_TEST = os.environ.get("DATABASE_URL_TEST")
DATABASE_URL = os.environ.get("DATABASE_URL")


class DatabaseConnector:
    connection = None
    # connection: psycopg2.connection
    engine = None

    @classmethod
    def get_connection(cls):
        if cls.connection is not None and cls.connection.closed == 0:
            print("Connected to the PostgreSQL database!")
            return cls.connection

        print("Connecting to the PostgreSQL database...")
        database_url = DATABASE_URL
        if not database_url:
            raise ValueError("DATABASE_URL is not set")

        cls.connection = psycopg2.connect(database_url)
        return cls.connection

    @classmethod
    def get_engine(cls):
        if cls.engine is None:
            from sqlalchemy import create_engine

            cls.engine = create_engine(
                DATABASE_URL,
                echo=False,
            )
        return cls.engine

    @classmethod
    def get_session(cls):
        cls.get_engine()
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=cls.get_engine(), expire_on_commit=False)
        return Session()
