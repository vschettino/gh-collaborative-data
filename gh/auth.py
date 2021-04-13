import os
import random

from dotenv import load_dotenv

load_dotenv()


def get_github_tokens() -> list:
    token_string = os.getenv("GITHUB_PATS", "")
    return token_string.split(",")


TOKENS = get_github_tokens()


def get_random_github_token():
    return random.choice(TOKENS)


def get_next_github_token(index: int) -> str:
    """
    Get the next token while there's still a new token. When the system requests more
    token than available, the sequence begins again
    """
    tokens = get_github_tokens()
    if index < len(tokens):
        return tokens[index]
    return tokens[index - len(tokens)]


def get_database_connection_string() -> str:
    password = os.getenv("POSTGRES_ROOT_PASSWORD", "")
    address = os.getenv("DATABASE_ADDRESS", "localhost")
    return f"postgresql+psycopg2://postgres:{password}@{address}:5432/postgres"
