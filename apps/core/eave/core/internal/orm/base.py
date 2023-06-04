import typing

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
