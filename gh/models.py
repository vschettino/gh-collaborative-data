from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def from_gh_objects(cls, objs, *args):
        result = []
        for obj in objs:
            model = cls.from_gh_object(obj, *args)
            if model:
                result.append(model)
        return result

    @classmethod
    def from_gh_object(cls, obj, *args):
        pass


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    login = Column(String, unique=True)
    url = Column(String)
    location = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    utc_locale = Column(String)
    country = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    @classmethod
    def from_gh_object(cls, user, repo=None):
        model = User(
            id=user.id,
            name=user.name,
            login=user.login,
            url=user.url,
            location=user.location,
        )
        extra = UserRepository.from_gh_object(user, repo)
        if extra:
            model.repositories.append(extra)
        return model


class UserRepository(BaseModel):
    __tablename__ = "user_repository"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), primary_key=True)
    contributions = Column(Integer)
    user = relationship("User", backref="repositories")
    repository = relationship("Repository", backref="users")

    @classmethod
    def from_gh_object(cls, user, repo):
        if not user.contributions:
            return
        return UserRepository(
            user_id=user.id,
            repository_id=repo.id,
            contributions=user.contributions,
        )


class UserOrganization(BaseModel):
    __tablename__ = "user_organization"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    contributions = Column(Integer)
    user = relationship("User", backref="organizations")
    organization = relationship("Organization", backref="users")


class Repository(BaseModel):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    url = Column(String)
    full_name = Column(String, unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

    organization = relationship("Organization", backref="repositories")
    owner = relationship("User", backref="owned_repositories")

    @classmethod
    def from_gh_object(cls, repo, *args):
        return Repository(
            id=repo.id,
            name=repo.name,
            full_name=repo.full_name,
            description=repo.description,
            url=repo.url,
            owner=User.from_gh_object(repo.owner, *args),
            organization=Organization.from_gh_object(repo.organization),
        )


class Organization(BaseModel):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    @classmethod
    def from_gh_object(cls, org):
        if not org:
            return
        return Organization(
            id=org.id,
            name=org.name,
        )


class PullRequest(BaseModel):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    title = Column(String)
    url = Column(String)
    body = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    repository_id = Column(Integer, ForeignKey("repositories.id"))

    user = relationship("User", backref="pulls")
    repository = relationship("Repository", backref="pulls")

    @classmethod
    def from_gh_object(cls, pull, repo):
        return PullRequest(
            id=pull.id,
            number=pull.number,
            title=pull.title,
            url=pull.url,
            body=pull.body,
            created_at=pull.created_at,
            updated_at=pull.updated_at,
            repository_id=repo.id,
            user=User.from_gh_object(pull.user),
        )


class Issue(BaseModel):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    title = Column(String)
    url = Column(String)
    body = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    repository_id = Column(Integer, ForeignKey("repositories.id"))

    user = relationship("User", backref="issues")
    repository = relationship("Repository", backref="repositories")

    @classmethod
    def from_gh_object(cls, issue, repo):
        return Issue(
            id=issue.id,
            number=issue.number,
            title=issue.title,
            url=issue.url,
            body=issue.body,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            repository_id=repo.id,
            user=User.from_gh_object(issue.user),
        )


class IssueComment(BaseModel):
    __tablename__ = "issue_comments"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    issue_id = Column(Integer, ForeignKey("issues.id"))

    user = relationship("User", backref="issue_comments")
    issue = relationship("Issue", backref="comments")

    @classmethod
    def from_gh_object(cls, comment, issue):
        return IssueComment(
            id=comment.id,
            url=comment.url,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            issue_id=issue.id,
            user=User.from_gh_object(comment.user),
        )


class PullRequestComment(BaseModel):
    __tablename__ = "pull_request_comments"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"))

    user = relationship("User", backref="pull_request_comments")
    pull_request = relationship("PullRequest", backref="comments")

    @classmethod
    def from_gh_object(cls, comment, pull):
        return PullRequestComment(
            id=comment.id,
            url=comment.url,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            pull_request_id=pull.id,
            user=User.from_gh_object(comment.user),
        )


class Interaction(BaseModel):
    """
    Materialized view that gathers all types of interactions
    """

    __tablename__ = "interactions"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), primary_key=True)
    created_at = Column(DateTime)
    type = Column(String)
    url = Column(String)


class Token(BaseModel):
    """
    Personal Access Tokens (PAT) used to authenticate into GitHub API
    """

    __tablename__ = "tokens"
    token = Column(String, primary_key=True)
    email = Column(String, nullable=True)
