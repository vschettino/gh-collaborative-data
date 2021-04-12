import logging
import sys
from datetime import datetime
from multiprocessing import Pool

from github import Github
from rich.logging import RichHandler
from rich.traceback import install
from sqlalchemy.dialects.postgresql.dml import OnConflictDoNothing
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import Insert
from urllib3 import Retry

import models as m
from db import engine
from dump import (
    get_issues,
    get_issues_comments,
    get_project,
    get_project_contributors,
    get_pull_requests,
    get_pulls_comments,
)
from hacks import authenticate

install()
logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] %(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)],
)


@compiles(Insert, "postgresql")
def prefix_inserts(insert, compiler, **kw):
    """
    - https://docs.sqlalchemy.org/en/14/core/compiler.html
    - https://stackoverflow.com/questions/33307250/postgresql-on-conflict-in-sqlalchemy/62305344#62305344
    """
    insert._post_values_clause = OnConflictDoNothing()
    return compiler.visit_insert(insert, **kw)


def start(projects: list, since: datetime):
    logger = logging.getLogger("Dump")
    logger.info(f"Start dumping {len(projects)} projects from {since.isoformat()}")
    params = []
    for worker in range(len(projects)):
        params.append((projects[worker], since))
    with Pool(len(projects)) as p:
        p.map(dump, params)


def dump(data):
    project, since = data
    logger = logging.getLogger("Dump:" + project)

    session = sessionmaker(bind=engine)(autoflush=True)
    retry_config = Retry(
        total=sys.maxsize, status_forcelist=(403, 429), backoff_factor=5
    )
    g = Github(per_page=100, retry=retry_config)
    # Ugliest hack I ever done in Python
    g._Github__requester._Requester__authenticate = authenticate

    repo = get_project(g, project)

    session.add(m.Repository.from_gh_object(repo))
    session.commit()

    contributors = get_project_contributors(repo)
    session.add_all(m.User.from_gh_objects(contributors, repo))
    session.commit()

    pulls = get_pull_requests(repo, since)
    session.add_all(m.PullRequest.from_gh_objects(pulls, repo))
    session.commit()

    issues = get_issues(repo, since)
    session.add_all(m.Issue.from_gh_objects(issues, repo))
    session.commit()

    for issue, comments in get_issues_comments(issues):
        session.add_all(m.IssueComment.from_gh_objects(comments, issue))

    for pull, comments in get_pulls_comments(pulls):
        session.add_all(m.PullRequestComment.from_gh_objects(comments, pull))

    session.commit()

    logger.info(f"dumped {len(contributors)} main contributors")
    logger.info(f"dumped {len(pulls)} PRs")
    logger.info(f"dumped {len(issues)} Issues")


if __name__ == "__main__":
    start(
        [
            "niklasf/python-chess",
            "tensorflow/tensorflow",
            "rails/rails",
            "clojure/clojure",
            "astropy/astropy",
            "django/django",
            "facebook/react",
            "golang/go",
            "kubernetes/kubernetes",
        ],
        since=datetime(2019, 1, 1),
    )
