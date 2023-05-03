import importlib
import os
import typing
from sqlalchemy import ForeignKeyConstraint, MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def _load_all() -> None:
    """
    This is meant to be used for scripts (eg Alembic or tests), where Base.metadata has to be fully populated.
    """
    import importlib
    import os

    dirname = os.path.dirname(os.path.abspath(__file__))

    for f in os.listdir(dirname):
        if f != "__init__.py" and os.path.isfile(f"{dirname}/{f}") and f[-3:] == ".py":
            module_name, _ = os.path.splitext(f)
            importlib.import_module(f"eave.core.internal.orm.{module_name}")

_base_metadata: typing.Optional[MetaData] = None

def get_base_metadata() -> MetaData:
    global _base_metadata
    if _base_metadata is None:
        _load_all()
        _base_metadata = Base.metadata

    return _base_metadata




