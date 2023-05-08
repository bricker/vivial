"""empty message

Revision ID: 7dfaabb0760c
Revises: b806fa046c93
Create Date: 2023-03-26 13:04:00.244959

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7dfaabb0760c"
down_revision = "b806fa046c93"
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
            column_name="id",
            server_default=sa.text("gen_random_uuid()"),
        )


def downgrade() -> None:
    for table in ["team", "access_requests", "document_references", "subscriptions", "confluence_destinations"]:
        op.alter_column(
            table_name=table,
            column_name="id",
            server_default=None,
        )
