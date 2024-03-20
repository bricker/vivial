# isort: off

import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.database import init_database
from eave.stdlib.config import SHARED_CONFIG

import asyncio
import logging

import eave.core.internal
import eave.core.internal.orm
import eave.core.internal.orm.base

from eave.stdlib.logging import eaveLogger


async def main() -> None:
    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    eaveLogger.fprint(logging.INFO, f"> EAVE_DB_NAME: {CORE_API_APP_CONFIG.db_name}")

    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {eave.core.internal.database.async_engine.url}")

    eaveLogger.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the {CORE_API_APP_CONFIG.db_name} database:",
    )
    eaveLogger.fprint(logging.WARNING, "- 💥 DELETES THE DATABASE 💥 (if it exists)")
    eaveLogger.fprint(logging.WARNING, "- (RE-)CREATES THE DATABASE")

    answer = input(
        eaveLogger.f(
            logging.WARNING, f"Proceed to delete and (re-)create the {CORE_API_APP_CONFIG.db_name} database? (Y/n) "
        )
    )
    if answer != "Y":
        print("Aborting.")
        return

    await init_database()


if __name__ == "__main__":
    asyncio.run(main())
