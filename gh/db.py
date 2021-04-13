from sqlalchemy import create_engine

from gh.auth import get_database_connection_string

engine = create_engine(get_database_connection_string())
