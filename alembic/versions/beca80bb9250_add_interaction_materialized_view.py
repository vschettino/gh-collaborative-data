"""Add Interaction materialized view

Revision ID: beca80bb9250
Revises: 4479d18b570c
Create Date: 2021-04-13 13:50:16.107383

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "beca80bb9250"
down_revision = "4479d18b570c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE MATERIALIZED VIEW interactions AS
            SELECT url, user_id, repository_id, created_at, 'Issue' as type
            FROM issues
        UNION
            select url, user_id, repository_id, created_at, 'Pull Request'
            from pull_requests
        UNION
            select prc.url, prc.user_id, pr.repository_id, prc.created_at, 'Issue Comment'
            from pull_request_comments prc
                     INNER JOIN pull_requests pr on pr.id = prc.pull_request_id
        UNION
            select ic.url, ic.user_id, i.repository_id, ic.created_at, 'Issue Comment'
            from issue_comments ic
                     INNER JOIN issues i on i.id = ic.issue_id
        """
    )


def downgrade():
    op.execute("DROP MATERIALIZED VIEW interactions")
