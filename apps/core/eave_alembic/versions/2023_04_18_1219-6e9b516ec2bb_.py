"""empty message

Revision ID: 6e9b516ec2bb
Revises: f2904b33fe71
Create Date: 2023-04-18 12:19:49.016806

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "6e9b516ec2bb"
down_revision = "f2904b33fe71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("alter type authprovider add value 'atlassian'")


def downgrade() -> None:
    pass
