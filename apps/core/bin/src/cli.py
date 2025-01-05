# isort: off

import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio
import logging
import os

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

import alembic
import alembic.command
import alembic.config
import alembic.migration
import alembic.script
import click

from eave.core.database import async_engine
from eave.core._database_setup import get_base_metadata, install_extensions, reset_database
from eave.core.config import CORE_API_APP_CONFIG
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER

_alembic_config = alembic.config.Config("alembic.ini")


@click.group()
def cli() -> None:
    pass


@cli.group()
def db() -> None:
    pass


@db.command()
def run_migrations() -> None:
    alembic.command.history(
        config=_alembic_config,
        indicate_current=True,
    )

    LOGGER.fprint(logging.WARNING, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    LOGGER.fprint(logging.WARNING, f"> Postgres connection URI: {async_engine.url}")

    LOGGER.fprint(logging.WARNING, "Running DB migrations!")
    answer = input(LOGGER.f(logging.WARNING, "Proceed? (y/n) "))

    if answer != "Y":
        raise click.Abort()

    alembic.command.upgrade(
        revision="head",
        config=_alembic_config,
    )


@db.command()
@click.option("-m", "--message", required=True)
def create_revision(message: str) -> None:
    alembic.command.revision(
        config=_alembic_config,
        message=message,
        autogenerate=True,
    )


@db.command()
def init_dev() -> None:
    LOGGER.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    LOGGER.fprint(logging.INFO, f"> Postgres connection URI: {async_engine.url}")

    LOGGER.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the '{async_engine.url.database}' database:",
    )
    LOGGER.fprint(logging.WARNING, f"- 💥 DELETES THE '{async_engine.url.database}' DATABASE 💥 (if it exists)")
    LOGGER.fprint(logging.WARNING, f"- (RE-)CREATES THE '{async_engine.url.database}' DATABASE")

    answer = input(LOGGER.f(logging.WARNING, f"Proceed to delete and (re-)create the '{async_engine.url.database}' database? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    async_engine.echo = True

    async def _run() -> None:
        await reset_database(async_engine)

        # This is necessary to detach the connections from the engine so that alembic can use the engine to stamp the database.
        await async_engine.dispose()

    asyncio.run(_run())

    alembic.command.stamp(
        config=_alembic_config,
        revision="head",
    )

@db.command()
def init_cloudsql() -> None:
    LOGGER.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    LOGGER.fprint(logging.INFO, f"> Postgres connection URI: {async_engine.url}")

    LOGGER.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the '{async_engine.url.database}' database:",
    )
    LOGGER.fprint(logging.WARNING, f"- Grants owner permission on the '{async_engine.url.database}' database to the app service account")
    LOGGER.fprint(logging.WARNING, "- Installs the necessary Postgres extensions")
    LOGGER.fprint(logging.WARNING, "- creates the tables using Base.create_all (NOT using migrations)")
    LOGGER.fprint(logging.WARNING, "- stamps the alembic revision")

    answer = input(LOGGER.f(logging.WARNING, "Proceed? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    async_engine.echo = True

    async def _run() -> None:
        # First, we create an engine for the postgres root user, connected to the eave database.
        cloudsql_tunnel_root_user_engine = create_async_engine(
            async_engine.url._replace(
                host=os.getenv("CLOUDSQL_TUNNEL_DB_HOST", "localhost"),
                port=int(os.getenv("CLOUDSQL_TUNNEL_DB_PORT", "5430")),
                username="postgres",
                password=os.environ["POSTGRES_ROOT_USER_PASSWORD"],
            ),
            isolation_level="AUTOCOMMIT",
            echo=True,
        )

        # Install the extensions while connected to the eave database
        # This is necessary so that the eave database gets the postgis tables.
        await install_extensions(cloudsql_tunnel_root_user_engine)

        # Now, update the engine to connect to the 'postgres' database, so that we can grant permissions to the app service account.
        cloudsql_tunnel_root_user_engine.url = cloudsql_tunnel_root_user_engine.url._replace(database="postgres")

        async with cloudsql_tunnel_root_user_engine.begin() as connection:
            # Temporarily give the 'postgres' root user the app service account role, so that it can manage its permissions
            await connection.execute(sqlalchemy.text(f'GRANT "{async_engine.url.username}" TO "{cloudsql_tunnel_root_user_engine.url.username}"'))

            # Grant the app service account ownership of the primary database
            await connection.execute(sqlalchemy.text(f'ALTER DATABASE "{async_engine.url.database}" OWNER TO "{async_engine.url.username}"'))

            # Undo the first command for least privileges policy
            await connection.execute(sqlalchemy.text(f'REVOKE "{async_engine.url.username}" FROM "{cloudsql_tunnel_root_user_engine.url.username}"'))

        await cloudsql_tunnel_root_user_engine.dispose()

        async with async_engine.begin() as connection:
            # Finally, create the tables in the 'eave' database
            await connection.run_sync(get_base_metadata().create_all)

        # Detach the connections from the engine so alembic can use it later.
        await async_engine.dispose()

    asyncio.run(_run())

    alembic.command.stamp(
        config=_alembic_config,
        revision="head",
    )


@db.command()
def create_tables() -> None:
    LOGGER.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    LOGGER.fprint(logging.INFO, f"> Postgres connection URI: {async_engine.url}")

    LOGGER.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the '{async_engine.url.database}' database:",
    )
    LOGGER.fprint(logging.WARNING, "- Creates the tables using Base.metadata (NOT using migrations)")

    answer = input(LOGGER.f(logging.WARNING, "Proceed to create the tables? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    async_engine.echo = True

    async def _run() -> None:
        async with async_engine.begin() as connection:
            await connection.run_sync(get_base_metadata().create_all)

        # Detach the active connections from the engine so that alembic can use the engine to stamp.
        await async_engine.dispose()

    asyncio.run(_run())

    alembic.command.stamp(
        config=_alembic_config,
        revision="head",
    )


@db.command()
def drop_tables() -> None:
    LOGGER.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    LOGGER.fprint(logging.INFO, f"> EAVE_DB_NAME: {async_engine.url.database}")

    LOGGER.fprint(logging.INFO, f"> Postgres connection URI: {async_engine.url}")

    LOGGER.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the '{async_engine.url.database}' database:",
    )
    LOGGER.fprint(logging.WARNING, "- DROPS ALL TABLES using Base.metadata")

    answer = input(LOGGER.f(logging.WARNING, f"Proceed to DROP ALL TABLES from the '{async_engine.url.database}' database? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    async_engine.echo = True

    async def _run() -> None:
        async with async_engine.begin() as connection:
            await connection.run_sync(get_base_metadata().drop_all)

        await async_engine.dispose()

    asyncio.run(_run())

if __name__ == "__main__":
    cli()
