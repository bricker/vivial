import asyncio
import os
import socket
from dotenv import load_dotenv

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import eave.core.internal
import eave.core.internal.orm
import eave.core.internal.orm.base
from eave.stdlib.core_api.models.team import DocumentPlatform


load_dotenv(f"{os.getenv('EAVE_HOME')}/.env", override=True)

EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")

# Some attempts to prevent this script from running against the production database
assert os.getenv("GAE_ENV") is None
assert os.getenv("GOOGLE_CLOUD_PROJECT") != "eave-production"
assert os.getenv("GCLOUD_PROJECT") != "eave-production"
assert EAVE_DB_NAME is not None
assert EAVE_DB_NAME != "eave"


async def init_database() -> None:
    """
    https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
    """
    # We can't connect to the database being created because, well, it doesn't exist.
    # Instead, connect to the postgres database on the host.
    postgres_uri = eave.core.internal.database.async_engine.url._replace(database="postgres")
    postgres_engine = create_async_engine(postgres_uri, isolation_level="AUTOCOMMIT")

    async with postgres_engine.begin() as connection:
        stmt = f'DROP DATABASE IF EXISTS "{EAVE_DB_NAME}"'
        await connection.execute(sqlalchemy.text(stmt))
        stmt = f'CREATE DATABASE "{EAVE_DB_NAME}"'
        await connection.execute(sqlalchemy.text(stmt))

    await postgres_engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
