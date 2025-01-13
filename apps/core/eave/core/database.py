import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.util
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import CORE_API_APP_CONFIG

DB_DRIVERNAME = "postgresql+asyncpg"

db_uri = sqlalchemy.engine.url.URL.create(
    drivername=DB_DRIVERNAME,
    host=CORE_API_APP_CONFIG.db_host,
    port=CORE_API_APP_CONFIG.db_port,
    username=CORE_API_APP_CONFIG.db_user,
    password=CORE_API_APP_CONFIG.db_pass,
    database=CORE_API_APP_CONFIG.db_name,
)

async_engine = create_async_engine(
    db_uri,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "timezone": "UTC",
            "application_name": "core-api",
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
