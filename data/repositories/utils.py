from datetime import datetime, timedelta
from database.db import DatabaseConnector
import uuid
import hashlib


def list_tuple_to_dict(tuple_key, rows):
    result = list(dict(zip(tuple_key, row)) for row in rows)
    return result
