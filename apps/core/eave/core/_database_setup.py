from eave.stdlib.config import SHARED_CONFIG

if SHARED_CONFIG.is_local:
    import importlib
    import os

    import sqlalchemy
    from sqlalchemy import MetaData
    from sqlalchemy.ext.asyncio import create_async_engine

    from eave.core.config import CORE_API_APP_CONFIG
    from eave.core.database import async_engine
    from eave.core.orm.base import Base

    def _load_all() -> None:
        """
        This is meant to be used for scripts (eg Alembic or tests), where Base.metadata has to be fully populated.
        """

        dirname = os.path.dirname(os.path.abspath(__file__)) + "/orm"
        dirents = os.listdir(dirname)

        for f in dirents:
            fname, ext = os.path.splitext(f)

            if ext == ".py" and f not in {"__init__.py", "base.py"}:
                importlib.import_module(f"eave.core.orm.{fname}")

    _base_metadata: MetaData | None = None

    def get_base_metadata() -> MetaData:
        global _base_metadata
        if _base_metadata is None:
            _load_all()
            _base_metadata = Base.metadata

        return _base_metadata

    async def init_database(db_name: str = CORE_API_APP_CONFIG.db_name) -> None:
        """
        This function DROPS the database (EAVE_DB_NAME)!

        https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
        """

        # Some attempts to prevent this script from running against the production database
        assert os.getenv("GAE_ENV") is None
        assert os.getenv("GCLOUD_PROJECT") != "eave-production"
        assert SHARED_CONFIG.google_cloud_project != "eave-production"
        assert SHARED_CONFIG.is_local
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
            await connection.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS postgis"))
            await connection.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS address_standardizer"))

        await create_database_tables(db_name)

    async def create_database_tables(db_name: str = CORE_API_APP_CONFIG.db_name) -> None:
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

    async def drop_database_tables(db_name: str) -> None:
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
            await connection.run_sync(get_base_metadata().drop_all)
