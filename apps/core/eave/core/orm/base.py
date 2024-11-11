from typing import Literal, Self
from uuid import UUID
from sqlalchemy import MetaData, Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    async def validate_or_exception(self) -> None:
        pass

    async def save(self, session: AsyncSession) -> Self:
        await self.validate_or_exception()
        session.add(self)
        await session.flush()
        return self

    @classmethod
    async def find_by_id(cls, session: AsyncSession, id: UUID) -> Self:
        return await session.get_one(cls, id)

    @classmethod
    def select(cls) -> Select[tuple[Self]]:
        return select(cls)

def _load_all() -> None:
    """
    This is meant to be used for scripts (eg Alembic or tests), where Base.metadata has to be fully populated.
    """
    import importlib
    import os

    dirname = os.path.dirname(os.path.abspath(__file__))
    dirents = os.listdir(dirname)

    for f in dirents:
        fname, ext = os.path.splitext(f)

        if ext == ".py" and f not in {"__init__.py", "base.py"}:
            importlib.import_module(f"eave.core.orm.{fname}")


_base_metadata: MetaData | None = None


def get_base_metadata() -> MetaData:
    global _base_metadata
    if _base_metadata is None:
        _load_all()
        _base_metadata = Base.metadata

    return _base_metadata
