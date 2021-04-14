import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def get_database_connection_string() -> str:
    password = os.getenv("POSTGRES_ROOT_PASSWORD", "")
    address = os.getenv("DATABASE_ADDRESS", "localhost")
    return f"postgresql+psycopg2://postgres:{password}@{address}:5432/postgres"


engine = create_engine(get_database_connection_string())
