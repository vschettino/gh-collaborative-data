import logging
from datetime import datetime

from github import (
    Github,
    Issue,
    IssueComment,
    NamedUser,
    PullRequest,
    PullRequestComment,
    Repository,
)


def get_project(g: Github, project_name) -> Repository:
    logger = logging.getLogger("GetProject")
    logger.info(f"{project_name}")
    return g.get_repo(project_name)


def get_project_contributors(repo: Repository, limit: int = 0) -> list[NamedUser]:
    contribs = []
    logger = logging.getLogger("GetProjectCollaborators")
    for contrib in repo.get_contributors():
        if limit and len(contribs) >= limit:
            return contribs
        logger.info(
            f"{contrib.login} from {contrib.location} with {contrib.contributions} contributions"
        )
        contribs.append(contrib)
    return contribs


def get_pull_requests(repo: Repository, since: datetime) -> list[PullRequest]:
    prs = []
    logger = logging.getLogger("GetPullRequests")
    for pull in repo.get_pulls(sort="created", direction="desc", state="all"):
        if pull.created_at < since:
            return prs
        logger.info(
            f"#{pull.number} from {repo.name} ({pull.created_at.isoformat()} by {pull.user.login})"
        )
        prs.append(pull)
    return prs


def get_issues(repo: Repository, since: datetime) -> list[Issue]:
    issues = []
    logger = logging.getLogger("GetIssues")
    for issue in repo.get_issues(sort="created", direction="desc", state="all"):
        if issue.created_at < since:
            return issues
        logger.info(
            f"#{issue.number} from {repo.name} ({issue.created_at.isoformat()})"
        )
        issues.append(issue)
    return issues


def get_issues_comments(issues: list[Issue]):
    comments = []
    for issue in issues:
        comments.append((issue, get_issue_comments(issue)))
    return comments


def get_issue_comments(issue: Issue) -> list[IssueComment]:
    logger = logging.getLogger("GetIssueComments")
    comments = list(issue.get_comments())
    logger.info(f"#{issue.number} ({len(comments)} items)")
    return comments


def get_pulls_comments(pulls: list[PullRequest]) -> list[PullRequestComment]:
    comments = []
    for pull in pulls:
        comments.append((pull, get_pull_comments(pull)))
    return comments


def get_pull_comments(pull: PullRequest) -> list[PullRequestComment]:
    logger = logging.getLogger("GetPullComments")
    comments = list(pull.get_comments()) + list(pull.get_issue_comments())
    logger.info(f"#{pull.number} ({len(comments)} items)")
    return comments
