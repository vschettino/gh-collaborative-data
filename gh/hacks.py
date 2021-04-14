import logging

from gh.auth import GitHubAuthentication

logger = logging.getLogger("Requester")
logger.setLevel("DEBUG")


def authenticate(url, requestHeaders, parameters):
    """
    Ugly hack to allow the Github Client use a random token for each request.
    Like that it is possible to parallelize dumps of a given project.
    """
    a = GitHubAuthentication()
    token = a.get_random_github_token()
    logger.info(f"request {url} using token ******{token[-5:]}")
    requestHeaders["Authorization"] = f"token {token}"
