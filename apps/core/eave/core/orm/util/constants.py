from sqlalchemy import ForeignKeyConstraint, text

PG_UUID_EXPR = text("(gen_random_uuid())")

PG_EMPTY_ARRAY_EXPR = text("'{}'")

ACCOUNTS_FK_CONSTRAINT = ForeignKeyConstraint(
    ["account_id"],
    ["accounts.id"],
    ondelete="CASCADE",
)
