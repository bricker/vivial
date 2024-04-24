
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
    # QueryParams = typing.TypedDict("QueryParams", {})
    # QueryParamsType: typing.TypeAlias = QueryParams

    # @classmethod
    # async def one_or_exception(cls, session: AsyncSession, **kwargs: typing.Unpack[QueryParamsType]) -> typing.Self:
    #     lookup = cls.query(**kwargs).limit(1)
    #     result = (await session.scalars(lookup)).one()
    #     return result

    # @classmethod
    # async def one_or_none(cls, session: AsyncSession, **kwargs: typing.Unpack[QueryParamsType]) -> typing.Self | None:
    #     lookup = cls.query(**kwargs).limit(1)
    #     result = await session.scalar(lookup)
    #     return result

    # @classmethod
    # def query(cls, **kwargs: typing.Unpack[QueryParamsType]) -> Select[typing.Tuple[typing.Self]]:
    #     raise NotImplementedError()


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

        if ext == ".py" and f != "__init__.py" and f != "base.py":
            importlib.import_module(f"eave.core.internal.orm.{fname}")


_base_metadata: MetaData | None = None


def get_base_metadata() -> MetaData:
    global _base_metadata
    if _base_metadata is None:
        _load_all()
        _base_metadata = Base.metadata

    return _base_metadata
