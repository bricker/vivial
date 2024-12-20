from enum import StrEnum

from sqlalchemy import text

PG_UUID_EXPR = text("(gen_random_uuid())")

PG_EMPTY_ARRAY_EXPR = text("'{}'")


class OnDeleteOption(StrEnum):
    """
    https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK
    """

    CASCADE = "CASCADE"
    SET_NULL = "SET NULL"
    SET_DEFAULT = "SET DEFAULT"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


CASCADE_ALL_DELETE_ORPHAN = "all, delete-orphan"
