import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import app_config

_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None
_sync_session_factory: sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session] | None = None


def get_engine() -> AsyncEngine:
    global _engine

    if _engine is not None:
        return _engine

    db_uri = sqlalchemy.engine.url.URL.create(
        drivername=app_config.db_driver,
        host=app_config.db_host,
        username=app_config.db_user,
        database=app_config.db_name,
    )

    _engine = create_async_engine(db_uri, echo=True)
    return _engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session_factory

    if _async_session_factory is not None:
        return _async_session_factory

    engine = get_engine()
    _async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _async_session_factory


def get_async_session() -> AsyncSession:
    factory = get_async_session_factory()
    return factory()


def get_sync_session_factory() -> sqlalchemy.orm.sessionmaker[sqlalchemy.orm.Session]:
    global _sync_session_factory

    if _sync_session_factory is not None:
        return _sync_session_factory

    engine = get_engine()
    _sync_session_factory = sqlalchemy.orm.sessionmaker(engine.sync_engine, expire_on_commit=False)
    return _sync_session_factory


def get_sync_session() -> sqlalchemy.orm.Session:
    factory = get_sync_session_factory()
    return factory()
