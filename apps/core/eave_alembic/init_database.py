import os

import dotenv
import eave.core.internal.orm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
import eave.core.internal.orm.base

dotenv.load_dotenv()

EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")

# Some attempts to prevent this script from running against the production database
assert os.getenv("GAE_ENV") is None
assert os.getenv("GOOGLE_CLOUD_PROJECT") != "eave-production"
assert os.getenv("GCLOUD_PROJECT") != "eave-production"
assert EAVE_DB_NAME is not None
assert EAVE_DB_NAME != "eave"

import asyncio
import socket

import eave.core.internal
import eave.stdlib.core_api
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


async def init_database() -> None:
    """
    https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
    """

    await create_database()
    await seed_database()


async def create_database() -> None:
    # We can't connect to the database being created because, well, it doesn't exist.
    # Instead, connect to the postgres database on the host.
    postgres_uri = eave.core.internal.database.db_uri._replace(database="postgres")
    postgres_engine = create_async_engine(postgres_uri, isolation_level="AUTOCOMMIT")

    async with postgres_engine.begin() as connection:
        stmt = f'DROP DATABASE IF EXISTS "{EAVE_DB_NAME}"'
        await connection.execute(sqlalchemy.text(stmt))
        stmt = f'CREATE DATABASE "{EAVE_DB_NAME}"'
        await connection.execute(sqlalchemy.text(stmt))

    await postgres_engine.dispose()


async def seed_database() -> None:
    async with eave.core.internal.database.async_engine.begin() as connection:
        await connection.run_sync(eave.core.internal.orm.base.get_base_metadata().create_all)

    session = AsyncSession(eave.core.internal.database.async_engine)

    team = eave.core.internal.orm.TeamOrm(
        name=f"{socket.gethostname()}", document_platform=eave.stdlib.core_api.enums.DocumentPlatform.confluence
    )
    session.add(team)
    await session.commit()
    await session.refresh(team)  # this is necessary to populate team.id

    # seed w/ eave slack team info
    slack_install = SlackInstallationOrm(
        team_id=team.id,
        slack_team_id="T03G5LV6R7Y",
        bot_token=os.getenv("SLACK_BOT_TOKEN", "empty"),
    )
    session.add(slack_install)
    await session.commit()

    await session.close()
    await eave.core.internal.database.async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
