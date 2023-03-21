import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine, AsyncSession
from .config import app_config

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None

async def get_engine() -> AsyncEngine:
    global _engine

    if _engine is not None:
        return _engine

    if app_config.db_connection_string is not None:
        db_uri = sqlalchemy.make_url(app_config.db_connection_string)
    else:
        assert app_config.db_driver is not None

        db_user = await app_config.db_user
        db_pass = await app_config.db_pass

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
