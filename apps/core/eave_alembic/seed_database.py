import asyncio
import os
import sys
import time
import socket
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import eave.core.internal
import eave.core.internal.orm as orm
import eave.core.internal.orm.base
from eave.stdlib.core_api.models.connect import AtlassianProduct
from eave.stdlib.core_api.models.team import DocumentPlatform

"""
This script is for seeding your local database with a bunch of garbage
data to help test SQL query performance.

None of the created table rows are valid data, other than the
foreign keys linking correctly.

UNDER NO CIRCUMSTANCES SHOULD THIS BE EVER RUN AGAINST PROD
"""

load_dotenv(f"{os.getenv('EAVE_HOME')}/.env", override=True)

EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")

# Some attempts to prevent this script from running against the production database
assert os.getenv("GAE_ENV") is None
assert os.getenv("GOOGLE_CLOUD_PROJECT") != "eave-production"
assert os.getenv("GCLOUD_PROJECT") != "eave-production"
assert EAVE_DB_NAME is not None
assert EAVE_DB_NAME != "eave"


async def seed_database() -> None:
    print(f"Starting to seed your db {EAVE_DB_NAME}...")
    async with eave.core.internal.database.async_engine.begin() as connection:
        await connection.run_sync(eave.core.internal.orm.base.get_base_metadata().create_all)

    session = AsyncSession(eave.core.internal.database.async_engine)

    num_rows = 1000

    # setup toolbar
    curr_progress = f"[0/{num_rows}] :: Seconds remaining: ???"
    sys.stdout.write(curr_progress)
    sys.stdout.flush()

    for row in range(num_rows):
        start = time.perf_counter()
        team = orm.TeamOrm(
            name=f"{socket.gethostname()}{row}",
            document_platform=DocumentPlatform.confluence,
        )
        session.add(team)
        await session.commit()
        await session.refresh(team) # necessary to populate team.id

        # NOTE: not seeding any Subscription objects rn

        slack = orm.SlackInstallationOrm(
            team_id=team.id,
            slack_team_id=f"slack_team_id{row}",
            bot_token="bot_token",
            bot_refresh_token="bot_refresh_token",
            bot_token_exp=None,
        )
        session.add(slack)

        github = orm.GithubInstallationOrm(
            team_id=team.id,
            github_install_id=f"github_install_id{row}",
        )
        session.add(github)

        atlassian = orm.AtlassianInstallationOrm(
            team_id=team.id,
            atlassian_cloud_id=f"atlassian_cloud_id{row}",
            oauth_token_encoded="oauth_token_encoded",
        )
        session.add(atlassian)

        connect_jira = orm.ConnectInstallationOrm(
            team_id=team.id,
            product=AtlassianProduct.jira,
            client_key=f"client_key{row}",
            shared_secret="shared_secret",
            base_url="base_url",
            org_url=f"org_url{row}",
            atlassian_actor_account_id="atlassian_actor_account_id",
            display_url=None,
            description=None,
        )
        session.add(connect_jira)

        connect_confluence = orm.ConnectInstallationOrm(
            team_id=team.id,
            product=AtlassianProduct.confluence,
            client_key=f"client_key{row}",
            shared_secret="shared_secret",
            base_url="base_url",
            org_url=f"org_url{row}",
            atlassian_actor_account_id="atlassian_actor_account_id",
            display_url=None,
            description=None,
        )
        session.add(connect_confluence)

        await session.commit()
        end = time.perf_counter()
        elapsed = end - start

        # update the progress tracker
        sys.stdout.write("\r") # return to start of line
        sys.stdout.write(" " * len(curr_progress)) # clear old chars from buffer
        sys.stdout.write("\r") # re-return to start of line
        curr_progress = f"[{row+1}/{num_rows}] :: Seconds remaining: ~{elapsed * (num_rows - row):.1f}"
        sys.stdout.write(curr_progress)
        sys.stdout.flush()

    await session.close()
    await eave.core.internal.database.async_engine.dispose()
    print("\nYour database has been seeded!")


if __name__ == "__main__":
    asyncio.run(seed_database())
