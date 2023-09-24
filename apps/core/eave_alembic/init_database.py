import asyncio
import logging
import os
from dotenv import load_dotenv

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

import eave.core.internal
import eave.core.internal.orm
import eave.core.internal.orm.base

from eave.stdlib.logging import eaveLogger

load_dotenv(f"{os.getenv('EAVE_HOME')}/.env", override=False)

EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
GAE_ENV = os.getenv("GAE_ENV")

eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {GOOGLE_CLOUD_PROJECT}")
eaveLogger.fprint(logging.INFO, f"> EAVE_DB_NAME: {EAVE_DB_NAME}")

# Some attempts to prevent this script from running against the production database
assert GAE_ENV is None
assert GOOGLE_CLOUD_PROJECT != "eave-production"
assert GCLOUD_PROJECT != "eave-production"
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
    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {eave.core.internal.database.async_engine.url}")

    eaveLogger.fprint(
        logging.WARNING, f"\nThis script will perform the following operations on the {EAVE_DB_NAME} database:"
    )
    eaveLogger.fprint(logging.WARNING, "- 💥 DELETES THE DATABASE 💥 (if it exists)")
    eaveLogger.fprint(logging.WARNING, "- (RE-)CREATES THE DATABASE")

    answer = input(
        eaveLogger.f(logging.WARNING, f"Proceed to delete and (re-)create the {EAVE_DB_NAME} database? (Y/n) ")
    )
    if answer != "Y":
        print("Aborting.")
        return

    answer = input(eaveLogger.f(logging.WARNING, "Really? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    async with postgres_engine.begin() as connection:
        stmt = f'DROP DATABASE IF EXISTS "{EAVE_DB_NAME}"'
        await connection.execute(sqlalchemy.text(stmt))
        stmt = f'CREATE DATABASE "{EAVE_DB_NAME}"'
        await connection.execute(sqlalchemy.text(stmt))

    await postgres_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
