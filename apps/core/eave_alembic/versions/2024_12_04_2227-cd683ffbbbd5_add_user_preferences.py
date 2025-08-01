"""add user preferences

Revision ID: cd683ffbbbd5
Revises: 786f1ff4f5bd
Create Date: 2024-12-04 22:27:29.135403

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cd683ffbbbd5"
down_revision = "786f1ff4f5bd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "outing_preferences",
        sa.Column("id", sa.Uuid(), server_default=sa.text("(gen_random_uuid())"), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("open_to_bars", sa.Boolean(), nullable=True),
        sa.Column("activity_category_ids", postgresql.ARRAY(sa.Uuid(), dimensions=1), nullable=True),
        sa.Column("restaurant_category_ids", postgresql.ARRAY(sa.Uuid(), dimensions=1), nullable=True),
        sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
    )
    op.add_column("activities", sa.Column("activity_category_id", sa.Uuid(), nullable=False))
    op.drop_column("activities", "subcategory_id")
    op.add_column("eventbrite_events", sa.Column("vivial_activity_category_id", sa.Uuid(), nullable=False))
    op.add_column("eventbrite_events", sa.Column("vivial_activity_format_id", sa.Uuid(), nullable=False))
    op.drop_column("eventbrite_events", "subcategory_id")
    op.drop_column("eventbrite_events", "format_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    pass
