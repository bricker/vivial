from typing import Optional
from sqlalchemy import (
    ForeignKeyConstraint,
    MetaData,
    PrimaryKeyConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def make_team_composite_pk() -> PrimaryKeyConstraint:
    return PrimaryKeyConstraint(
        "team_id",
        "id",
    )

def make_team_fk() -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["team_id"],
        ["teams.id"],
    )


def make_team_composite_fk(fk_column: str, foreign_table: str) -> ForeignKeyConstraint:
    return ForeignKeyConstraint(["team_id", fk_column], [f"{foreign_table}.team_id", f"{foreign_table}.id"])


UUID_DEFAULT_EXPR = text("(gen_random_uuid())")

def _load_all() -> None:
    """
    This is meant to be used for scripts (eg Alembic or tests), where Base.metadata has to be fully populated.
    """
    import os
    import importlib
    dirname = os.path.dirname(os.path.abspath(__file__))

    for f in os.listdir(dirname):
        if f != "__init__.py" and os.path.isfile(f"{dirname}/{f}") and f[-3:] == ".py":
            module_name, _ = os.path.splitext(f)
            importlib.import_module(f"eave.core.internal.orm.{module_name}")

_base_metadata: Optional[MetaData] = None
def get_base_metadata() -> MetaData:
    global _base_metadata
    if _base_metadata is None:
        _load_all()
        _base_metadata = Base.metadata

    return _base_metadata
