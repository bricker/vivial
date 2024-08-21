"""
This script is for seeding your local database with a bunch of garbage
data to help test SQL query performance.

None of the created table rows are valid data, other than the
foreign keys linking correctly.

UNDER NO CIRCUMSTANCES SHOULD THIS BE EVER RUN AGAINST PROD
"""

# ruff: noqa: S311

# isort: off

import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import argparse
import asyncio
import logging
import os
import random
import socket
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from google.cloud.bigquery import SchemaField, SqlTypeNames

import eave.core.internal
import eave.core.internal.orm.base
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm, MetabaseInstanceState
from eave.core.internal.orm.team import TeamOrm, bq_dataset_id
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import LogContext, eaveLogger
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT

_EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")
_GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
_GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
_GAE_ENV = os.getenv("GAE_ENV")

# Some attempts to prevent this script from running against the production database
assert _GAE_ENV is None
assert _GOOGLE_CLOUD_PROJECT != "eave-production"
assert _GCLOUD_PROJECT != "eave-production"

_empty_ctx = LogContext()

def make_bq_view(*, team_id: uuid.UUID, view_id: str, friendly_name: str, description: str) -> None:
    bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.construct_table(
        dataset_id=bq_dataset_id(team_id),
        table_id=view_id,
    )

    bq_view.description = description
    bq_view.friendly_name = friendly_name
    bq_view.view_query = """
    select
        "Field A" as field_a,
        "Field B" as field_b,
        123 as field_c
    """

    bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_table(
        table=bq_view,
        ctx=_empty_ctx,
    )

    bq_view.schema = (
        SchemaField(
            name="field_a",
            description="this is field_a!",
            field_type=SqlTypeNames.STRING,
        ),
        SchemaField(
            name="field_b",
            description="this is field_b!",
            field_type=SqlTypeNames.STRING,
        ),
        SchemaField(
            name="field_c",
            description="this is field_c!",
            field_type=SqlTypeNames.INTEGER,
        ),
    )

    EAVE_INTERNAL_BIGQUERY_CLIENT.update_table(
        table=bq_view,
        ctx=_empty_ctx,
    )

async def seed_table_entries_for_team(team_id: uuid.UUID, row: int, session: AsyncSession) -> None:
    creds = await ClientCredentialsOrm.create(
        session=session,
        team_id=team_id,
        scope=ClientScope.readwrite,
        description=f"credentials for team {team_id} (database seed)",
    )

    await ClientCredentialsOrm.query(session=session, params=ClientCredentialsOrm.QueryParams(team_id=team_id))

    creds.scope = ClientScope.readwrite
    await session.flush()

    metabase_instance = await MetabaseInstanceOrm.create(
        session=session,
        team_id=team_id,
        state=MetabaseInstanceState.READY,
    )

    # Hardcoded signing key for easier development. This is also hardcoded in the metabase environment variables in share.metabase.env.
    metabase_instance.jwt_signing_key = "unsafe"
    await session.flush()

    EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_dataset(dataset_id=bq_dataset_id(team_id))

    for eavent in range(10):
        words = ["foo", "bar", "bazz", "fizz", "buzz", "far", "fuzz", "bizz", "boo", "fazz"]
        readable_name = f"Dummy event {row}.{eavent}"
        rand_desc = " ".join([words[random.randint(0, len(words) - 1)] for _ in range(random.randint(5, 40))])
        view_id = f"{row}_{eavent}"

        await VirtualEventOrm.create(
            session=session,
            team_id=team_id,
            view_id=view_id,
            readable_name=readable_name,
            description=rand_desc,
        )

        try:
            make_bq_view(team_id=team_id, view_id=view_id, friendly_name=readable_name, description=rand_desc)
        except Exception:
            eaveLogger.warning("BigQuery error. Dummy view not created.")


async def seed_database(db: AsyncEngine, team_id: uuid.UUID | None = None) -> None:
    session = AsyncSession(db)

    # only need to create entries for 1 team if team_id to seed is provided
    # FIXME: This used to be 100 but it was taking way too long to create all the dummy views in BQ.
    # Also this is buggy because it was running `seed_table_entries_for_team` 100 times with the same team
    num_rows = 1 if team_id is None else 1

    # setup progress bar
    curr_progress = f"[0/{num_rows}] :: Seconds remaining: ???"
    sys.stdout.write(curr_progress)
    sys.stdout.flush()

    team: TeamOrm | None = None

    if team_id:
        team = await TeamOrm.one_or_exception(session=session, team_id=team_id)

    for row in range(num_rows):
        start = time.perf_counter()

        if not team:
            team = await TeamOrm.create(
                session=session,
                name=f"{socket.gethostname()}{row}",
                allowed_origins=["*"],
            )

        await seed_table_entries_for_team(team_id=team.id, row=row, session=session)

        end = time.perf_counter()
        elapsed = end - start

        # update the progress tracker
        sys.stdout.write("\r")  # return to start of line
        sys.stdout.write(" " * len(curr_progress))  # clear old chars from buffer
        sys.stdout.write("\r")  # re-return to start of line
        curr_progress = f"[{row+1}/{num_rows}] :: Seconds remaining: ~{elapsed * (num_rows - row):.1f}"
        sys.stdout.write(curr_progress)
        sys.stdout.flush()

    await session.commit()
    await session.close()
    await db.dispose()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Database seeder")
    parser.add_argument("-t", "--team_id", help="ID of an existing team to seed", type=uuid.UUID, required=False)
    parser.add_argument(
        "-d", "--database", help="Name of the database to seed", type=str, required=False, default=_EAVE_DB_NAME
    )
    args, _ = parser.parse_known_args()

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

    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {_GOOGLE_CLOUD_PROJECT}")
    eaveLogger.fprint(logging.INFO, f"> Target Database: {seed_db.url.database}")
    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {seed_db.url}")
    if args.team_id:
        eaveLogger.fprint(logging.WARNING, f"\nThis script will insert junk seed data for the {args.team_id} team.")
    else:
        eaveLogger.fprint(
            logging.WARNING, f"\nThis script will insert junk seed data into the {seed_db.url.database} database."
        )

    answer = input(
        eaveLogger.f(
            logging.WARNING, f"Proceed to insert junk seed data into the {seed_db.url.database} database? (Y/n) "
        )
    )
    if answer != "Y":
        eaveLogger.fprint(logging.CRITICAL, "Aborting.")
        return

    eaveLogger.fprint(logging.INFO, f"Starting to seed your db {seed_db.url.database}...")
    await seed_database(db=seed_db, team_id=args.team_id)
    eaveLogger.fprint(logging.INFO, "\nYour database has been seeded!")


if __name__ == "__main__":
    asyncio.run(main())
