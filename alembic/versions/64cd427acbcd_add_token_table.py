"""Add token table

Revision ID: 64cd427acbcd
Revises: beca80bb9250
Create Date: 2021-04-14 14:35:53.579417

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "64cd427acbcd"
down_revision = "beca80bb9250"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tokens",
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("token"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tokens")
    # ### end Alembic commands ###