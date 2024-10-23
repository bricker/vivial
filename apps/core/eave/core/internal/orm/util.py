from sqlalchemy import text

PG_UUID_EXPR = text("(gen_random_uuid())")

PG_EMPTY_ARRAY_EXPR = text("'{}'")
