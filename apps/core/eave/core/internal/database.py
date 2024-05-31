import os

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.util
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from eave.core.internal.orm.base import get_base_metadata
from eave.stdlib.config import SHARED_CONFIG, EaveEnvironment

from .config import CORE_API_APP_CONFIG

db_uri = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
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

if SHARED_CONFIG.eave_env in [EaveEnvironment.development, EaveEnvironment.test]:

    async def init_database(db_name: str = CORE_API_APP_CONFIG.db_name) -> None:
        """
        This function DROPS the database (EAVE_DB_NAME)!

        https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
        """

        # Some attempts to prevent this script from running against the production database
        assert os.getenv("GAE_ENV") is None
        assert os.getenv("GCLOUD_PROJECT") != "eave-production"
        assert SHARED_CONFIG.google_cloud_project != "eave-production"
        assert SHARED_CONFIG.eave_env in [EaveEnvironment.development, EaveEnvironment.test]
        assert db_name not in [None, "eave", "eave-production"]

        # We can't connect to the database being created because, well, it doesn't exist (or it's going to be dropped).
        # Instead, connect to the postgres database on the host.
        postgres_uri = async_engine.url._replace(database="postgres")
        postgres_engine = create_async_engine(
            postgres_uri,
            isolation_level="AUTOCOMMIT",
            echo=False,
            connect_args={
                "server_settings": {
                    "timezone": "UTC",
                },
            },
        )

        async with postgres_engine.begin() as connection:
            await connection.execute(sqlalchemy.text(f'DROP DATABASE IF EXISTS "{db_name}"'))
            await connection.execute(sqlalchemy.text(f'CREATE DATABASE "{db_name}"'))
            await connection.execute(sqlalchemy.text(f'ALTER DATABASE "{db_name}" SET timezone TO "UTC"'))

            try:
                await connection.execute(sqlalchemy.text("""CREATE ROLE "eave-agent" PASSWORD 'dev'"""))
            except Exception as e:
                # FIXME: asyncpg.exceptions.DuplicateObjectError is the correct error to catch here, but masked by sqlalchemy
                print("eave-agent user already exists.", e)

        await postgres_engine.dispose()

        # create schema in the target db
        target_db_uri = async_engine.url._replace(database=db_name)
        target_engine = create_async_engine(
            target_db_uri,
            isolation_level="AUTOCOMMIT",
            echo=False,
            connect_args={
                "server_settings": {
                    "timezone": "UTC",
                },
            },
        )

        async with target_engine.begin() as connection:
            # create tables in empty db
            await connection.run_sync(get_base_metadata().create_all)

            # install pg_trgm extension (used for some fuzzy match operations)
            try:
                await connection.execute(sqlalchemy.text("CREATE EXTENSION pg_trgm"))
            except Exception as e:
                print("pg_trgm already installed.", e)
