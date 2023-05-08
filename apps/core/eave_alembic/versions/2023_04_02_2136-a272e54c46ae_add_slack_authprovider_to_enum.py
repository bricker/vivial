"""add slack authprovider to enum

Revision ID: a272e54c46ae
Revises: c88077c78b60
Create Date: 2023-04-02 21:36:28.279210

"""
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a272e54c46ae"
down_revision = "c88077c78b60"
branch_labels = None
depends_on = None

new_type = sa.Enum("google", "slack", name="auth_provider")
old_type = sa.Enum("google", name="auth_provider")
tcr = sa.sql.table("accounts", sa.Column("auth_provider", new_type, nullable=False))


def upgrade():
    # op.alter_column("accounts", "auth_provider", type_=new_type, existing_type=old_type)
    # op.execute("ALTER TYPE authprovider ADD VALUE 'slack'")
    pass


def downgrade():
    # this is destructive to the validity of the data... soooo never do it
    # op.execute(tcr.update().where(tcr.c.authprovider == "slack").values(authprovider="google"))
    # op.alter_column("accounts", "auth_provider", type_=old_type, existing_type=new_type)
    pass
