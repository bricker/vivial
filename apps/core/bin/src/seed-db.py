# isort: off

import sys
sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files
load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.team import TeamOrm

import asyncio
import logging
import os
import time
import socket

from sqlalchemy.ext.asyncio import AsyncSession

import eave.core.internal
import eave.core.internal.orm.base
from eave.stdlib.logging import eaveLogger

"""
This script is for seeding your local database with a bunch of garbage
data to help test SQL query performance.

None of the created table rows are valid data, other than the
foreign keys linking correctly.

UNDER NO CIRCUMSTANCES SHOULD THIS BE EVER RUN AGAINST PROD
"""

_EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")
_GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
_GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
_GAE_ENV = os.getenv("GAE_ENV")

eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {_GOOGLE_CLOUD_PROJECT}")
eaveLogger.fprint(logging.INFO, f"> EAVE_DB_NAME: {_EAVE_DB_NAME}")

# Some attempts to prevent this script from running against the production database
assert _GAE_ENV is None
assert _GOOGLE_CLOUD_PROJECT != "eave-production"
assert _GCLOUD_PROJECT != "eave-production"
assert _EAVE_DB_NAME is not None
assert _EAVE_DB_NAME != "eave"


async def seed_database() -> None:
    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {eave.core.internal.database.async_engine.url}")
    eaveLogger.fprint(logging.WARNING, f"\nThis script will insert junk seed data into the {_EAVE_DB_NAME} database.")

    answer = input(
        eaveLogger.f(logging.WARNING, f"Proceed to insert junk seed data into the {_EAVE_DB_NAME} database? (Y/n) ")
    )
    if answer != "Y":
        print("Aborting.")
        return

    print(f"Starting to seed your db {_EAVE_DB_NAME}...")
    session = AsyncSession(eave.core.internal.database.async_engine)

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
        team_id = team.id

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
    await eave.core.internal.database.async_engine.dispose()
    print("\nYour database has been seeded!")


if __name__ == "__main__":
    asyncio.run(seed_database())
