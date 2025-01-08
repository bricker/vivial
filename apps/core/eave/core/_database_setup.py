from sqlalchemy.ext.asyncio import AsyncEngine

from eave.stdlib.config import SHARED_CONFIG

if SHARED_CONFIG.is_local:
    import importlib
    import os

    import sqlalchemy
    from sqlalchemy import MetaData
    from sqlalchemy.ext.asyncio import create_async_engine

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

    async def reset_database(engine: AsyncEngine = async_engine) -> None:
        """
        This function DROPS the database (EAVE_DB_NAME)!

        https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
        """

        # Some attempts to prevent this script from running against the production database
        assert os.getenv("GCLOUD_PROJECT") != "eave-production"
        assert os.getenv("GOOGLE_CLOUD_PROJECT") != "eave-production"
        assert os.getenv("EAVE_DEPLOY_TARGET") != "eave-production"
        assert SHARED_CONFIG.google_cloud_project != "eave-production"
        assert SHARED_CONFIG.is_local

        # We can't connect to the database being created because, well, it doesn't exist (or it's going to be dropped).
        # Instead, connect to the postgres database on the host.
        postgres_engine = create_async_engine(
            engine.url._replace(database="postgres"),
            isolation_level="AUTOCOMMIT",
            echo=engine.echo,
        )

        async with postgres_engine.begin() as connection:
            await connection.execute(sqlalchemy.text(f'DROP DATABASE IF EXISTS "{engine.url.database}"'))
            await connection.execute(sqlalchemy.text(f'CREATE DATABASE "{engine.url.database}"'))
            await connection.execute(sqlalchemy.text(f'ALTER DATABASE "{engine.url.database}" SET timezone TO "UTC"'))

        await install_extensions(postgres_engine)
        await postgres_engine.dispose()

        async with engine.begin() as connection:
            await connection.run_sync(get_base_metadata().create_all)

    async def install_extensions(engine: AsyncEngine = async_engine) -> None:
        async with engine.begin() as connection:
            await connection.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS postgis"))
