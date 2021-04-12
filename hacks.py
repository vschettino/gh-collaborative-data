import logging

from auth import get_random_github_token

logger = logging.getLogger("Requester")
logger.setLevel("DEBUG")


def authenticate(url, requestHeaders, parameters):
    """
    Ugly hack to allow the Github Client use a random token for each request.
    Like that it is possible to parallelize dumps of a given project.
    """
    token = get_random_github_token()
    logger.info(f"using token ***{token[-5:]}")
    requestHeaders["Authorization"] = f"token {token}"
