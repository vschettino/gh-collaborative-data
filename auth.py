import os

from dotenv import load_dotenv

load_dotenv()


def get_github_tokens() -> list:
    token_string = os.getenv("GITHUB_PATS", "")
    return token_string.split(",")


def get_database_connection_string() -> str:
    password = os.getenv("POSTGRES_ROOT_PASSWORD", "")
    address = os.getenv("DATABASE_ADDRESS", "localhost")
    return f"postgresql+psycopg2://postgres:{password}@{address}:5432/postgres"
