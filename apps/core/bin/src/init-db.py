# isort: off

import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio
import logging

import eave.core.internal
import eave.core.internal.orm
import eave.core.internal.orm.base
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.database import init_database
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import eaveLogger


async def main(db_name: str) -> None:
    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {SHARED_CONFIG.google_cloud_project}")
    eaveLogger.fprint(logging.INFO, f"> EAVE_DB_NAME: {db_name}")

    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {eave.core.internal.database.async_engine.url}")

    eaveLogger.fprint(
        logging.WARNING,
        f"\nThis script will perform the following operations on the {db_name} database:",
    )
    eaveLogger.fprint(logging.WARNING, "- 💥 DELETES THE DATABASE 💥 (if it exists)")
    eaveLogger.fprint(logging.WARNING, "- (RE-)CREATES THE DATABASE")

    answer = input(
        eaveLogger.f(
            logging.WARNING, f"Proceed to delete and (re-)create the {db_name} database? (Y/n) "
        )
    )
    if answer != "Y":
        print("Aborting.")
        return

    await init_database(db_name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database initializer")
    parser.add_argument("-d", "--db_name", help="Name of database to reconstruct", type=str, required=False)
    args = parser.parse_args()

    db_name = args.db_name or CORE_API_APP_CONFIG.db_name
    asyncio.run(main(db_name))
