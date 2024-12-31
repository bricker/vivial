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
import datetime
import logging
import os
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

import eave.core.database
from eave.core.graphql.types.activity import ActivitySource
from eave.core.graphql.types.restaurant import RestaurantSource
from eave.core.lib.address import Address
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.orm.outing import OutingActivityOrm, OutingOrm, OutingReservationOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import OutingBudget
from eave.core.shared.geo import GeoPoint
from eave.stdlib.logging import LOGGER
from eave.stdlib.time import LOS_ANGELES_TIMEZONE

_EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")
_GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
_GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
_GAE_ENV = os.getenv("GAE_ENV")

# Some attempts to prevent this script from running against the production database
assert _GAE_ENV is None
assert _GOOGLE_CLOUD_PROJECT != "eave-production"
assert _GCLOUD_PROJECT != "eave-production"


async def seed_database(db: AsyncEngine, account_id: uuid.UUID | None) -> None:
    session = AsyncSession(db)

    num_rows = 100 if account_id is None else 1

    # setup progress bar
    curr_progress = f"[0/{num_rows}] :: Seconds remaining: ???"
    sys.stdout.write(curr_progress)
    sys.stdout.flush()

    account = None
    if account_id:
        account = await AccountOrm.get_one(session, account_id)

    for row in range(num_rows):
        start = time.perf_counter()

        visitor_id = str(uuid.uuid4())
        dummy_date = datetime.datetime.now() + datetime.timedelta(days=2)

        if not account_id:
            account = AccountOrm(
                session,
                email=f"john{row}@gmail.com",
                plaintext_password="pasword1!",  # noqa: S106
            )

        assert account is not None

        survey = SurveyOrm(
            session,
            visitor_id=visitor_id,
            account=account,
            start_time_utc=dummy_date,
            search_area_ids=[SearchRegionOrm.all()[0].id],
            budget=OutingBudget.EXPENSIVE,
            timezone=LOS_ANGELES_TIMEZONE,
            headcount=2,
        )

        outing = OutingOrm(
            session,
            visitor_id=visitor_id,
            survey=survey,
            account=account,
        )

        outing_activity = OutingActivityOrm(
            session,
            outing=outing,
            source_id=str(uuid.uuid4()),
            source=ActivitySource.INTERNAL,
            start_time_utc=dummy_date,
            timezone=LOS_ANGELES_TIMEZONE,
            headcount=2,
        )

        outing_reservation = OutingReservationOrm(
            session,
            outing=outing,
            source_id=str(uuid.uuid4()),
            source=RestaurantSource.GOOGLE_PLACES,
            start_time_utc=dummy_date,
            timezone=LOS_ANGELES_TIMEZONE,
            headcount=2,
        )

        reserver_details = ReserverDetailsOrm(
            session,
            account=account,
            first_name="Jeff",
            last_name="Goldbloom",
            phone_number="+12698675309",
        )

        booking = BookingOrm(
            session,
            outing=outing,
            accounts=[account],
            reserver_details=reserver_details,
        )

        booking.activities.append(
            BookingActivityTemplateOrm(
                session,
                booking=booking,
                source_id=str(uuid.uuid4()),
                source=ActivitySource.EVENTBRITE,
                name="Biking in McDonalds parking lot",
                start_time_utc=outing_activity.start_time_utc,
                timezone=LOS_ANGELES_TIMEZONE,
                photo_uri="https://s3-media0.fl.yelpcdn.com/bphoto/NQFmn6sxr2RC-czWIBi8aw/o.jpg",
                headcount=outing_activity.headcount,
                external_booking_link="https://micndontlds.com",
                address=Address(
                    address1="101 Mcdonald St",
                    address2="Unit 666",
                    city="LA",
                    state="CA",
                    country="USA",
                    zip_code="12345",
                ),
                coordinates=GeoPoint(
                    lat=0,
                    lon=0,
                ),
            )
        )

        booking.reservations.append(
            BookingReservationTemplateOrm(
                session,
                booking=booking,
                source_id=str(uuid.uuid4()),
                source=RestaurantSource.GOOGLE_PLACES,
                name="Red lobster dumpster",
                start_time_utc=outing_reservation.start_time_utc,
                timezone=LOS_ANGELES_TIMEZONE,
                photo_uri="https://s3-media0.fl.yelpcdn.com/bphoto/NQFmn6sxr2RC-czWIBi8aw/o.jpg",
                headcount=outing_reservation.headcount,
                external_booking_link="https://redlobster.yum",
                address=Address(
                    address1="3269 Abandoned Alley Way",
                    address2=None,
                    city="LA",
                    state="CA",
                    country="USA",
                    zip_code="12345",
                ),
                coordinates=GeoPoint(
                    lat=0,
                    lon=1,
                ),
            )
        )

        await session.flush()

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
    parser.add_argument(
        "-d",
        "--database",
        help="Name of the database to seed",
        type=str,
        required=False,
        default=_EAVE_DB_NAME,
    )
    parser.add_argument(
        "-a",
        "--account",
        help="Account ID to seed relations for",
        type=uuid.UUID,
        required=False,
        default=None,
    )
    args, _ = parser.parse_known_args()

    postgres_uri = eave.core.database.async_engine.url._replace(database=args.database)
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

    LOGGER.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {_GOOGLE_CLOUD_PROJECT}")
    LOGGER.fprint(logging.INFO, f"> Target Database: {seed_db.url.database}")
    LOGGER.fprint(logging.INFO, f"> Postgres connection URI: {seed_db.url}")
    LOGGER.fprint(
        logging.WARNING, f"\nThis script will insert junk seed data into the {seed_db.url.database} database."
    )

    warn_msg = f"Proceed to insert junk seed data into the {seed_db.url.database} database?"
    if args.account:
        warn_msg = f"Seeding for account {args.account}. {warn_msg}"

    answer = input(LOGGER.f(logging.WARNING, f"{warn_msg} (Y/n) "))
    if answer != "Y":
        LOGGER.fprint(logging.CRITICAL, "Aborting.")
        return

    LOGGER.fprint(logging.INFO, f"Starting to seed your db {seed_db.url.database}...")
    await seed_database(db=seed_db, account_id=args.account)
    LOGGER.fprint(logging.INFO, "\nYour database has been seeded!")


if __name__ == "__main__":
    asyncio.run(main())
