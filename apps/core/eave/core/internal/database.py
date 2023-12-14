import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.util
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import app_config

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=app_config.db_host,
    port=app_config.db_port,
    username=app_config.db_user,
    password=app_config.db_pass,
    database=app_config.db_name,
)
async_engine = create_async_engine(db_uri,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "timezone": "UTC",
        },
    },
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)
"""
:class:`sqlalchemy.ext.asyncio.AsyncSession` factory. Use with `begin()` to automatically
commit and close the session when the context manager exits.

Example::

    async with eave_db.async_session.begin() as db_session:
        db_session.add(some_object)

    print("session is automatically committed, some_object has been persisted.")
"""
