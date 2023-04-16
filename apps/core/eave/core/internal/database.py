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

    if app_config.db_connection_string is not None:
        db_uri = sqlalchemy.make_url(app_config.db_connection_string)
    else:
        assert app_config.db_driver is not None

        db_user = app_config.db_user
        db_pass = app_config.db_pass

        db_uri = sqlalchemy.engine.url.URL.create(
            drivername=app_config.db_driver,
            host=app_config.db_host,
            port=app_config.db_port,
            username=db_user,
            password=db_pass,
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
