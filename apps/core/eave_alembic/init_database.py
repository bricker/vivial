import os
import socket

from dotenv import load_dotenv

load_dotenv()

import asyncio

import eave.core.internal.database as eave_db
import eave.core.internal.orm
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models

# Protect against running this in production, sort of
assert os.getenv("GAE_ENV") is None


async def init_database() -> None:
    """
    https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
    """
    metadata = eave.core.internal.orm.Base.metadata
    asyncengine = eave_db.get_engine()

    async with asyncengine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    async with eave_db.get_async_session() as session:
        team = eave_orm.TeamOrm(
            name=f"{socket.gethostname()}", document_platform=eave_models.DocumentPlatform.confluence
        )

        session.add(team)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_database())
