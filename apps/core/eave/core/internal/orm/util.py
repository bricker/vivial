from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, text


UUID_DEFAULT_EXPR = text("(gen_random_uuid())")
