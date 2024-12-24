# isort: off

import math
import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

# isort: on

# ruff: noqa: E402

import asyncio
import csv
import os
import re

from sqlalchemy.dialects.postgresql import Range

from eave.core import database
from eave.core.lib.google_places import GoogleMapsUtility, GooglePlacesUtility
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.evergreen_activity import EvergreenActivityOrm, EvergreenActivityTicketTypeOrm, WeeklyScheduleOrm
from eave.stdlib.logging import LOGGER

header = "[Title, Description, Address, Images, Category, Subcategory, Format, Availability (Days & Hours), Duration (Minutes), Ticket Type A, Ticket Type A Cost, Ticket Type B, Ticket Type B Cost, Taxes, Service Fees, Bookable, Book URL]"


async def import_evergreen_activities() -> None:
    with open(os.path.dirname(os.path.abspath(__file__)) + "/evergreen.csv") as f:  # noqa: ASYNC230
        rdr = csv.reader(f)
        i = 0
        for row in rdr:
            i += 1

            if i == 1:
                continue

            (
                title,
                description,
                address,
                images,
                category,
                subcategory,
                fmt,
                availability,
                duration,
                ticket_type_a,
                ticket_type_a_cost_dollars,
                ticket_type_b,
                ticket_type_b_cost,
                tax_percentage,
                fees_dollars,
                bookable,
                book_url,
            ) = row

            LOGGER.info(f"Importing `{title}`")

            activity_category = next((a for a in ActivityCategoryOrm.all() if a.name == subcategory), None)
            if not activity_category:
                raise Exception(f"no matching category for {subcategory}")

            images = images.split()
            bookable = bookable == "Yes"
            duration = int(duration)
            fmt = None if not fmt else fmt
            book_url = None if book_url == "N/A" else book_url
            tax_percentage = 0 if tax_percentage == "N/A" else int(tax_percentage)
            fees_dollars = 0 if fees_dollars == "N/A" else float(fees_dollars)

            maps = GoogleMapsUtility()
            geocode_results = maps.geocode(address=address)
            assert len(geocode_results) > 0
            geocode_result = geocode_results[0]
            place_id = geocode_result.get("place_id")
            assert place_id

            places = GooglePlacesUtility()
            google_place = await places.get_google_place(place_id)
            location = places.location_from_google_place(google_place)

            # geometry = geocode_result.get("geometry")
            # assert geometry
            # location = geometry.get("location")
            # assert location
            # lat = location.get("lat")
            # lon = location.get("lng")
            # assert lat is not None and lon is not None

            # coordinates = GeoPoint(
            #     lat=lat,
            #     lon=lon,
            # )

            ticket_type_a = None if ticket_type_a == "N/A" else ticket_type_a

            if ticket_type_a_cost_dollars == "N/A":
                ticket_type_a_cost_dollars = None
            else:
                ticket_type_a_cost_dollars = re.sub("^\\$", "", ticket_type_a_cost_dollars)
                ticket_type_a_cost_dollars = float(ticket_type_a_cost_dollars)

            availability = availability.split("\n")
            availability = [d.split(": ") for d in availability]

            spans: list[Range[int]] = []

            for day in availability:
                match day[0].strip():
                    case "Mon":
                        daynum = 0
                    case "Tues":
                        daynum = 1
                    case "Weds":
                        daynum = 2
                    case "Thurs":
                        daynum = 3
                    case "Fri":
                        daynum = 4
                    case "Sat":
                        daynum = 5
                    case "Sun":
                        daynum = 6
                    case _:
                        raise Exception(f"invalid day: {day[0]}")

                hours_text = day[1].strip()

                if hours_text == "CLOSED":
                    pass
                else:
                    spanleft, spanright = hours_text.split("-")
                    parsed_open = _parsetime(spanleft)
                    parsed_close = _parsetime(spanright)

                    hrstr_open, mnstr_open, apstr_open = parsed_open.groups()
                    hrstr_close, mnstr_close, apstr_close = parsed_close.groups()

                    hrint_open = _gethr(hrstr_open, apstr_open)
                    hrint_close = _gethr(hrstr_close, apstr_close)

                    daymnint_open = hrint_open * 60
                    daymnint_close = hrint_close * 60

                    if mnstr_open:
                        daymnint_open += int(re.sub(r"^:", "", mnstr_open))

                    if mnstr_close:
                        daymnint_close += int(re.sub(r"^:", "", mnstr_close))

                    if daymnint_close < daymnint_open:
                        daymnint_close += 24 * 60

                    week_maxmins = 7 * 24 * 60
                    weekminint_open = (daynum * 24 * 60) + daymnint_open
                    weekminint_close = (daynum * 24 * 60) + daymnint_close

                    if weekminint_close > week_maxmins:
                        spans.extend(
                            [
                                Range(weekminint_open, week_maxmins, bounds="[)"),
                                Range(0, weekminint_close % week_maxmins, bounds="[)"),
                            ]
                        )
                    else:
                        spans.append(Range(weekminint_open, weekminint_close, bounds="[)"))

            spans.sort(key=lambda span: span.lower if span.lower is not None else 0)

            async with database.async_session.begin() as session:
                activity = EvergreenActivityOrm(
                    session,
                    activity_category_id=activity_category.id,
                    address=location.address.to_address(),
                    booking_url=book_url,
                    coordinates=location.coordinates,
                    description=description,
                    duration_minutes=duration,
                    google_place_id=place_id,
                    is_bookable=bookable,
                    title=title,
                )

                WeeklyScheduleOrm(
                    session,
                    evergreen_activity=activity,
                    week_of=None,
                    minute_spans_local=spans,
                )

                if ticket_type_a is not None and ticket_type_a_cost_dollars is not None:
                    activity.ticket_types.append(
                        EvergreenActivityTicketTypeOrm(
                            session,
                            evergreen_activity=activity,
                            base_cost_cents=math.floor(ticket_type_a_cost_dollars * 100),
                            service_fee_cents=math.floor(fees_dollars * 100),
                            tax_percentage=tax_percentage,
                            title=ticket_type_a,
                        )
                    )

def _gethr(hrstr: str, ap: str) -> int:
    if ap == "AM":
        if hrstr == "12":
            return 0
        else:
            return int(hrstr)
    elif ap == "PM":
        if hrstr == "12":
            return 12
        else:
            return int(hrstr) + 12
    else:
        raise ValueError()


def _parsetime(timestr: str) -> re.Match[str]:
    m = re.match(r"(\d+)(:\d+)?(AM|PM)$", timestr)
    if not m:
        raise Exception(f"doesnt match re: {timestr}")
    return m


if __name__ == "__main__":
    asyncio.run(import_evergreen_activities())
