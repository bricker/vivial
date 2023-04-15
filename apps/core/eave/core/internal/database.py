import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import app_config

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def get_engine() -> AsyncEngine:
    global _engine

    if _engine is not None:
        return _engine

    db_uri = sqlalchemy.engine.url.URL.create(
        drivername=app_config.db_driver,
        host=app_config.db_host,
        port=app_config.db_port,
        username=app_config.db_user,
        password=app_config.db_pass,
        database=app_config.db_name,
    )

    _engine = create_async_engine(db_uri, echo=True)
    return _engine


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory

    if _session_factory is not None:
        return _session_factory

    engine = await get_engine()
    _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncSession:
    factory = await get_session_factory()
    return factory()
