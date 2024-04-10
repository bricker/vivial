# ruff: noqa: S311

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
import random
import socket
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

import eave.core.internal
import eave.core.internal.orm.base
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm
from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import eaveLogger


async def seed_table_entries_for_team(team_id: uuid.UUID, row: int, session: AsyncSession) -> None:
    await ClientCredentialsOrm.create(
        session=session,
        team_id=team_id,
        scope=ClientScope.readwrite,
        description=f"credentials for team {team_id} (database seed)",
    )

    github = GithubInstallationOrm(
        team_id=team_id,
        github_install_id=f"github_install_id{row}",
    )
    session.add(github)

    mb_inst = await MetabaseInstanceOrm.create(
        session=session,
        team_id=team_id,
    )
    mb_inst.update(
        session=session,
        route_id=uuid.uuid4(),
    )

    for eavent in range(30):
        words = ["foo", "bar", "bazz", "fizz", "buzz", "far", "fuzz", "bizz", "boo", "fazz"]
        rand_desc = " ".join([words[random.randint(0, len(words) - 1)] for _ in range(random.randint(5, 40))])
        await VirtualEventOrm.create(
            session=session,
            team_id=team_id,
            view_id=f"{row}.{eavent}",
            readable_name=f"Dummy event {row}.{eavent}",
            description=rand_desc,
        )


async def seed_database(db: AsyncEngine) -> None:
    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {db.url}")
    eaveLogger.fprint(logging.WARNING, f"\nThis script will insert junk seed data into the {db.url.database} database.")

    answer = input(
        eaveLogger.f(logging.WARNING, f"Proceed to insert junk seed data into the {db.url.database} database? (Y/n) ")
    )
    if answer != "Y":
        eaveLogger.fprint(logging.CRITICAL, "Aborting.")
        return

    eaveLogger.fprint(logging.INFO, f"Starting to seed your db {db.url.database}...")
    session = AsyncSession(db)

    num_rows = 100

    # setup progress bar
    curr_progress = f"[0/{num_rows}] :: Seconds remaining: ???"
    sys.stdout.write(curr_progress)
    sys.stdout.flush()

    for row in range(num_rows):
        start = time.perf_counter()
        team = TeamOrm(
            name=f"{socket.gethostname()}{row}",
        )
        session.add(team)
        await session.commit()
        await session.refresh(team)  # necessary to populate team.id

        await seed_table_entries_for_team(team_id=team.id, row=row, session=session)

        await session.commit()
        end = time.perf_counter()
        elapsed = end - start

        # update the progress tracker
        sys.stdout.write("\r")  # return to start of line
        sys.stdout.write(" " * len(curr_progress))  # clear old chars from buffer
        sys.stdout.write("\r")  # re-return to start of line
        curr_progress = f"[{row+1}/{num_rows}] :: Seconds remaining: ~{elapsed * (num_rows - row):.1f}"
        sys.stdout.write(curr_progress)
        sys.stdout.flush()

    await session.close()
    await db.dispose()
    eaveLogger.fprint(logging.INFO, "\nYour database has been seeded!")


async def seed_team(team_id: uuid.UUID, db: AsyncEngine) -> None:
    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {db.url}")
    eaveLogger.fprint(logging.WARNING, f"\nThis script will insert junk seed data into the {db.url.database} database.")

    answer = input(
        eaveLogger.f(
            logging.WARNING,
            f"Proceed to insert junk seed data for team {team_id} into the {db.url.database} database? (Y/n) ",
        )
    )
    if answer != "Y":
        eaveLogger.fprint(logging.CRITICAL, "Aborting.")
        return

    eaveLogger.fprint(logging.INFO, f"Starting to seed your db {db.url.database}...")
    session = AsyncSession(seed_db)

    # negative row to make sure it doesn't conflict with any other seeded entries already in db
    await seed_table_entries_for_team(team_id=team_id, row=-1, session=session)

    await session.commit()
    await session.close()
    await seed_db.dispose()
    eaveLogger.fprint(logging.INFO, "\nYour database has been seeded!")
    eaveLogger.fprint(
        logging.INFO,
        f"(You will need to manually set a valid value for MetabaseInstanceOrm.jwt_signing_key for team {team_id})",
    )


if __name__ == "__main__":
    _EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")
    _GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    _GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
    _GAE_ENV = os.getenv("GAE_ENV")

    import argparse


    parser = argparse.ArgumentParser(description="Database seeder")
    parser.add_argument("-t", "--team_id", help="ID of an existing team to seed", type=uuid.UUID, required=False)
    parser.add_argument("-d", "--database", help="Name of the database to seed", type=str, required=False, default=_EAVE_DB_NAME)
    args = parser.parse_args()

    postgres_uri = eave.core.internal.database.async_engine.url._replace(database=args.database)
    seed_db = create_async_engine(
        postgres_uri,
        isolation_level="AUTOCOMMIT",
        echo=False,
        connect_args={
            "server_settings": {
                "timezone": "UTC",
            },
        },
    )

    # ==== TRACING JUNK ====
    from eave.otel_tracing.nettracing.telem.instrumentors.instrument import eave_instrument_db
    eave_instrument_db(seed_db.sync_engine)
    # ==== END TRACING ====

    """
    This script is for seeding your local database with a bunch of garbage
    data to help test SQL query performance.

    None of the created table rows are valid data, other than the
    foreign keys linking correctly.

    UNDER NO CIRCUMSTANCES SHOULD THIS BE EVER RUN AGAINST PROD
    """

    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {_GOOGLE_CLOUD_PROJECT}")
    eaveLogger.fprint(logging.INFO, f"> Target Database: {seed_db.url.database}")

    # Some attempts to prevent this script from running against the production database
    assert _GAE_ENV is None
    assert _GOOGLE_CLOUD_PROJECT != "eave-production"
    assert _GCLOUD_PROJECT != "eave-production"
    assert seed_db.url.database is not None
    assert seed_db.url.database != "eave"

    if args.team_id:
        asyncio.run(seed_team(args.team_id, seed_db))
    else:
        asyncio.run(seed_database(seed_db))
