# isort: off

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio
from typing import Literal
from collections.abc import MutableMapping
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

import eave.core.database as eave_db
import eave.core.orm
import eave.core.orm.base
import eave.stdlib.time
from eave.core._database_setup import get_base_metadata

eave.stdlib.time.set_utc()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

target_metadata = get_base_metadata()

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _include_name(
    name: str | None,
    type_: Literal["schema", "table", "column", "index", "unique_constraint", "foreign_key_constraint"],
    parent_names: MutableMapping[
        Literal[
            "schema_name",
            "table_name",
            "schema_qualified_table_name",
        ],
        str | None,
    ],
) -> bool:
    if type_ == "table":
        # 'spatial_ref_sys' table is created by postgis, and not managed by SQLAlchemy
        return name not in ["spatial_ref_sys"]
    else:
        return True


async def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=eave_db.async_engine.url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=_include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_name=_include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    async with eave_db.async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await eave_db.async_engine.dispose()


if context.is_offline_mode():
    asyncio.run(run_migrations_offline())
else:
    asyncio.run(run_migrations_online())
