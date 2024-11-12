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

from eave.core.graphql.types.restaurant import RestaurantSource

sys.path.append(".")

from eave.core.graphql.types.activity import ActivitySource
from eave.core.orm.search_region import SearchRegionOrm
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
import eave.core.orm.base
from eave.core.orm.account import AccountOrm
from eave.core.orm.account_booking import AccountBookingOrm
from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.orm.outing import OutingOrm
from eave.core.orm.outing_activity import OutingActivityOrm
from eave.core.orm.outing_reservation import OutingReservationOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.survey import SurveyOrm
from eave.stdlib.logging import eaveLogger

_EAVE_DB_NAME = os.getenv("EAVE_DB_NAME")
_GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
_GCLOUD_PROJECT = os.getenv("GCLOUD_PROJECT")
_GAE_ENV = os.getenv("GAE_ENV")

# Some attempts to prevent this script from running against the production database
assert _GAE_ENV is None
assert _GOOGLE_CLOUD_PROJECT != "eave-production"
assert _GCLOUD_PROJECT != "eave-production"


async def seed_database(db: AsyncEngine) -> None:
    session = AsyncSession(db)

    num_rows = 100

    # setup progress bar
    curr_progress = f"[0/{num_rows}] :: Seconds remaining: ???"
    sys.stdout.write(curr_progress)
    sys.stdout.flush()

    for row in range(num_rows):
        start = time.perf_counter()

        visitor_id = uuid.uuid4()
        dummy_date = datetime.datetime.now() + datetime.timedelta(days=2)
        account = await AccountOrm.build(
            email=f"john{row}@gmail.com",
            plaintext_password="pasword1!",  # noqa: S106
        ).save(session)
        survey = await SurveyOrm.build(
            visitor_id=visitor_id,
            account_id=account.id,
            start_time=dummy_date,
            search_area_ids=[SearchRegionOrm.all()[0].id],
            budget=2,
            headcount=2,
        ).save(session)
        outing = await OutingOrm.build(
            visitor_id=visitor_id,
            survey_id=survey.id,
            account_id=account.id,
        ).save(session)
        outing_activity = await OutingActivityOrm.build(
            outing_id=outing.id,
            activity_id=str(uuid.uuid4()),
            activity_source=ActivitySource.INTERNAL,
            activity_start_time=dummy_date,
            num_attendees=2,
        ).save(session)
        outing_reservation = await OutingReservationOrm.build(
            outing_id=outing.id,
            reservation_id=str(uuid.uuid4()),
            reservation_source=RestaurantSource.GOOGLE_PLACES,
            reservation_start_time=dummy_date,
            num_attendees=2,
        ).save(session)
        reserver_details = await ReserverDetailsOrm.build(
            account_id=account.id,
            first_name="Jeff",
            last_name="Goldbloom",
            phone_number="+12698675309",
        ).save(session)
        booking = await BookingOrm.build(
            reserver_details_id=reserver_details.id,
        ).save(session)
        _account_booking = await AccountBookingOrm.build(
            account_id=account.id,
            booking_id=booking.id,
        ).save(session)
        _booking_activity_template = await BookingActivityTemplateOrm.build(
            booking_id=booking.id,
            activity_name="Biking in McDonalds parking lot",
            activity_start_time=outing_activity.activity_start_time,
            num_attendees=outing_activity.num_attendees,
            external_booking_link="https://micndontlds.com",
            activity_location_address1="101 Mcdonald St",
            activity_location_address2="Unit 666",
            activity_location_city="LA",
            activity_location_region="CA",
            activity_location_country="USA",
            activity_location_latitude=0,
            activity_location_longitude=0,
        ).save(session)
        _booking_reservation_template = await BookingReservationTemplateOrm.build(
            booking_id=booking.id,
            reservation_name="Red lobster dumpster",
            reservation_start_time=outing_reservation.reservation_start_time,
            num_attendees=outing_reservation.num_attendees,
            external_booking_link="https://redlobster.yum",
            reservation_location_address1="3269 Abandoned Alley Way",
            reservation_location_address2="",
            reservation_location_city="LA",
            reservation_location_region="CA",
            reservation_location_country="USA",
            reservation_location_latitude=0,
            reservation_location_longitude=1,
        ).save(session)

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
        "-d", "--database", help="Name of the database to seed", type=str, required=False, default=_EAVE_DB_NAME
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

    eaveLogger.fprint(logging.INFO, f"> GOOGLE_CLOUD_PROJECT: {_GOOGLE_CLOUD_PROJECT}")
    eaveLogger.fprint(logging.INFO, f"> Target Database: {seed_db.url.database}")
    eaveLogger.fprint(logging.INFO, f"> Postgres connection URI: {seed_db.url}")
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
    await seed_database(db=seed_db)
    eaveLogger.fprint(logging.INFO, "\nYour database has been seeded!")


if __name__ == "__main__":
    asyncio.run(main())
