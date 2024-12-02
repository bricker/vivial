# isort: off

from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
import os
import sys
from typing import Any

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio
import logging
import click

import alembic
import alembic.command
import alembic.config
import alembic.migration
import alembic.script

import eave.core.database
import eave.core.orm
import eave.core.orm.base
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.database import init_database, create_database_tables
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import eaveLogger

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

    eave_db_name = os.environ["EAVE_DB_NAME"]
    eave_db_host = os.environ["EAVE_DB_HOST"]
    eave_db_user = os.environ["EAVE_DB_USER"]
    google_cloud_project = os.environ["GOOGLE_CLOUD_PROJECT"]

    eaveLogger.fprint(logging.WARNING, "Running DB migrations!")
    eaveLogger.fprint(logging.WARNING, f"GOOGLE_CLOUD_PROJECT={google_cloud_project}")
    eaveLogger.fprint(logging.WARNING, f"EAVE_DB_HOST={eave_db_host}")
    eaveLogger.fprint(logging.WARNING, f"EAVE_DB_NAME={eave_db_name}")
    eaveLogger.fprint(logging.WARNING, f"EAVE_DB_USER={eave_db_user}")

    answer = input(eaveLogger.f(logging.WARNING, "Proceed? (Y/n) "))

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
@click.option("-d", "--database", required=False, default=CORE_API_APP_CONFIG.db_name)
def init_dev(database: str) -> None:
    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    eaveLogger.fprint(logging.INFO, f"> EAVE_DB_NAME: {database}")

    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {eave.core.database.async_engine.url}")

    eaveLogger.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the {database} database:",
    )
    eaveLogger.fprint(logging.WARNING, "- 💥 DELETES THE DATABASE 💥 (if it exists)")
    eaveLogger.fprint(logging.WARNING, "- (RE-)CREATES THE DATABASE")

    answer = input(eaveLogger.f(logging.WARNING, f"Proceed to delete and (re-)create the {database} database? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    asyncio.run(init_database(database))

    alembic.command.stamp(
        config=_alembic_config,
        revision="head",
    )


@db.command()
@click.option("-d", "--database", required=False, default=CORE_API_APP_CONFIG.db_name)
def create_tables(database: str) -> None:
    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    eaveLogger.fprint(logging.INFO, f"> EAVE_DB_NAME: {database}")

    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {eave.core.database.async_engine.url}")

    eaveLogger.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the {database} database:",
    )
    eaveLogger.fprint(logging.WARNING, "- Creates the tables using Base.metadata (not migrations)")

    answer = input(eaveLogger.f(logging.WARNING, "Proceed to create the tables? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    asyncio.run(create_database_tables(database))

    alembic.command.stamp(
        config=_alembic_config,
        revision="head",
    )


if __name__ == "__main__":
    cli()
