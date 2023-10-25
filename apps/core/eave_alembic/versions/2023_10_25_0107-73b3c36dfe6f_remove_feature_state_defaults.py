"""remove feature state defaults

Revision ID: 73b3c36dfe6f
Revises: ab1d261ea5ed
Create Date: 2023-10-25 01:07:33.537448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "73b3c36dfe6f"
down_revision = "ab1d261ea5ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("github_repos", "api_documentation_state", server_default=None)
    op.alter_column("github_repos", "inline_code_documentation_state", server_default=None)
    op.alter_column("github_repos", "architecture_documentation_state", server_default=None)
