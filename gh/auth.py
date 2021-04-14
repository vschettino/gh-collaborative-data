import logging
import random
from datetime import datetime

from sqlalchemy.orm import sessionmaker

from gh.db import engine
from gh.models import Token


class GitHubAuthentication:
    TOKEN_CACHE_SECONDS = 120

    def __init__(self):
        self.session = sessionmaker(engine)()
        self._tokens = []
        self._last_updated = None
        self.logger = logging.getLogger("GitHubAuth")

    @property
    def tokens(self) -> list:
        if self._tokens and self.is_cache_valid():
            return self._tokens
        self.refresh_tokens()
        return self._tokens

    def is_cache_valid(self) -> bool:
        now = datetime.now()
        cache_duration = (now - self._last_updated).seconds
        return self._last_updated and cache_duration < self.TOKEN_CACHE_SECONDS

    def get_random_github_token(self):
        return random.choice(self.tokens)

    def get_next_github_token(self, index: int) -> str:
        """
        Get the next token while there's still a new token. When the system requests more
        token than available, the sequence begins again
        """
        tokens = self.tokens
        if index < len(tokens):
            return tokens[index]
        return tokens[index - len(tokens)]

    def refresh_tokens(self):
        now = datetime.now()
        self.logger.warning(
            f"Actually fetching tokens from Database at {now.isoformat()}"
        )
        tokens = [item[0] for item in self.session.query(Token.token).all()]
        self.logger.warning(f"Fetched {len(tokens)} from Database")
        self._tokens = tokens
        self._last_updated = now
