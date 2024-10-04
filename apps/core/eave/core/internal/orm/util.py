from sqlalchemy import text

UUID_DEFAULT_EXPR = text("(gen_random_uuid())")
