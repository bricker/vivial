import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import app_config

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    host=app_config.db_host,
    username=app_config.db_user,
    database=app_config.db_name,
)

async_engine = create_async_engine(db_uri, echo=app_config.dev_mode)
sync_engine = sqlalchemy.create_engine(db_uri, echo=app_config.dev_mode)

sync_session = sqlalchemy.orm.sessionmaker(sync_engine, expire_on_commit=False)
"""
:class:`sqlalchemy.orm.Session` factory. Use with `begin()` to automatically
commit and close the session when the context manager exits.

Example::

    with eave_db.sync_session.begin() as db_session:
        db_session.add(some_object)

    print("session is automatically committed, some_object has been persisted.")
"""

async_session = async_sessionmaker(async_engine, expire_on_commit=False)
"""
:class:`sqlalchemy.ext.asyncio.AsyncSession` factory. Use with `begin()` to automatically
commit and close the session when the context manager exits.

Example::

    async with eave_db.async_session.begin() as db_session:
        db_session.add(some_object)

    print("session is automatically committed, some_object has been persisted.")
"""
