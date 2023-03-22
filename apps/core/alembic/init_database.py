import os

from dotenv import load_dotenv

load_dotenv()

import asyncio

import eave_core.internal.orm
from alembic import command, context
import eave_core.internal.database as eave_db

# FIXME: A better way to do this.
raise Exception("Do not run this against the production database. You can remove this line for development.")


async def init_database() -> None:
    """
    https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
    """
    metadata = eave_core.internal.orm.Base.metadata
    connectable = await eave_db.get_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(metadata.create_all)

    await connectable.dispose()

    alembic_config = context.config
    command.stamp(alembic_config, "head")


asyncio.run(init_database())
