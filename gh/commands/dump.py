import logging
import sys
from datetime import datetime
from multiprocessing import Pool

from github import Github
from sqlalchemy.dialects.postgresql.dml import OnConflictDoNothing
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import Insert
from urllib3 import Retry

import gh.models as m
from gh.commands.dump_helper import (
    get_issues,
    get_issues_comments,
    get_project,
    get_project_contributors,
    get_pull_requests,
    get_pulls_comments,
)
from gh.db import engine
from gh.hacks import authenticate

PROJECTS = [
    "niklasf/python-chess",
    "tensorflow/tensorflow",
    "rails/rails",
    "clojure/clojure",
    "astropy/astropy",
    "django/django",
    "facebook/react",
    "golang/go",
    "kubernetes/kubernetes",
    "urfave/cli",
    "grafana/grafana",
    "hashicorp/vault",
    "sqlalchemy/sqlalchemy",
]
SINCE = datetime(2019, 1, 1)


@compiles(Insert, "postgresql")
def prefix_inserts(insert, compiler, **kw):
    """
    - https://docs.sqlalchemy.org/en/14/core/compiler.html
    - https://stackoverflow.com/questions/33307250/postgresql-on-conflict-in-sqlalchemy/62305344#62305344
    """
    insert._post_values_clause = OnConflictDoNothing()
    return compiler.visit_insert(insert, **kw)


def start(*args, **kwargs):
    logger = logging.getLogger("Dump")
    logger.info(f"Start dumping {len(PROJECTS)} projects from {SINCE.isoformat()}")
    params = []
    for worker in range(len(PROJECTS)):
        params.append((PROJECTS[worker], SINCE))
    with Pool(len(PROJECTS)) as p:
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
