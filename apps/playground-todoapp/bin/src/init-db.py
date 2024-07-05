# isort: off

import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio

import sqlalchemy
from eave_playground.todoapp.orm import BaseOrm, async_engine
from sqlalchemy.ext.asyncio import create_async_engine


async def main() -> None:
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
        await connection.execute(sqlalchemy.text(f'DROP DATABASE IF EXISTS "{async_engine.url.database}"'))
        await connection.execute(sqlalchemy.text(f'CREATE DATABASE "{async_engine.url.database}"'))

    await postgres_engine.dispose()

    async with async_engine.begin() as connection:
        await connection.run_sync(BaseOrm.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
