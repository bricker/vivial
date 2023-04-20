import dotenv

dotenv.load_dotenv()

import os
import socket
import asyncio
import sqlalchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models

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
    url = eave_db.engine.url._replace(database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    async with engine.begin() as connection:
        stmt = f"CREATE DATABASE \"{EAVE_DB_NAME}\""
        await connection.execute(sqlalchemy.text(stmt))

    await engine.dispose()

    # Now we'll use our normal engine.
    async with eave_db.engine.begin() as connection:
        await connection.run_sync(eave_orm.Base.metadata.create_all)

    async with eave_db.get_async_session() as session:
        team = eave_orm.TeamOrm(
            name=f"{socket.gethostname()}", document_platform=eave_models.DocumentPlatform.confluence
        )

        session.add(team)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_database())
