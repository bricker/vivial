"""empty message

Revision ID: 7a7f21394cb7
Revises: 7dfaabb0760c
Create Date: 2023-03-26 13:27:32.394677

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7a7f21394cb7"
down_revision = "7dfaabb0760c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in [
        "access_requests",
        "confluence_destinations",
        "document_references",
        "subscriptions",
        "teams",
    ]:
        op.alter_column(
            table_name=table,
            column_name="created",
            server_default=sa.func.current_timestamp(),
        )


def downgrade() -> None:
    for table in ["team", "access_requests", "document_references", "subscriptions", "confluence_destinations"]:
        op.alter_column(
            table_name=table,
            column_name="created",
            server_default=None,
        )
