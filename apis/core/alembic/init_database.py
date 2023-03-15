import os
from dotenv import load_dotenv

load_dotenv()

import asyncio
from alembic import command

import eave.internal.orm
from alembic import context
from eave.internal.database import engine

# FIXME: A better way to do this.
raise Exception("Do not run this against the production database.")

async def init_database() -> None:
    """
    https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
    """
    metadata = eave.internal.orm.Base.metadata
    connectable = engine

    async with connectable.connect() as connection:
        await connection.run_sync(metadata.create_all)

    await connectable.dispose()

    alembic_config = context.config
    command.stamp(alembic_config, "head")

asyncio.run(init_database())