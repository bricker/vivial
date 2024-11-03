import asyncio
from datetime import datetime
import math
import os
from zoneinfo import ZoneInfo

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.eventbrite.client import EventbriteClient, OrderBy
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.venue import Venue
from eave.stdlib.geo import GeoCoordinates
from eave.stdlib.logging import LOGGER
from eave.stdlib.ranges import BoundRange
from eave.stdlib.util import unwrap

from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.core.internal.orm.eventbrite_event import EventbriteEventOrm
from eave.core.outing.constants.categories import get_vivial_subcategory_from_eventbrite_subcategory_id
from eave.core.outing.constants.areas import LOS_ANGELES_AREAS
from eave.core.outing.constants.formats import get_vivial_format_from_eventbrite_format_id
from eave.core.outing.models.geo_area import GeoArea

import eave.core.internal.database

# These are hand-picked by Vivial staff
_EVENTBRITE_ORGANIZER_IDS = [
    "46435628873",
]

def _exclude_event(event: Event) -> bool:
    return (
        event.get("online_event") is True
        or event.get("is_locked") is True
        or event.get("show_pick_a_seat") is True
        or event.get("is_sold_out") is True
        or event.get("category_id") is None
        or event.get("subcategory_id") is None
        or event.get("format_id") is None
    )

async def get_eventbrite_events() -> None:
    client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    for organizer_id in _EVENTBRITE_ORGANIZER_IDS:
        paginator = client.list_events_for_organizer(
            organizer_id=organizer_id,
            query={
                "order_by": OrderBy.start_asc,
                "status": EventStatus.live,
                "only_public": True,
                "expand": ",".join(
                    [
                        Expansion.ticket_availability,
                        Expansion.category,
                        Expansion.subcategory,
                        Expansion.event_sales_status,
                        Expansion.music_properties,
                        Expansion.venue,
                    ]
                ),
            },
        )

        async for batch in paginator:
            # FIXME: This will ignore events that may have previously been added into the database, if their settings were changed to become excluded.
            events = [event for event in batch if not _exclude_event(event)]

            async with eave.core.internal.database.async_session.begin() as db_session:
                for event in events:
                    if (eventbrite_event_id := event.get("id")) is None:
                        continue
                    if not (event_name := event.get("name")):
                        continue
                    if (venue := event.get("venue")) is None:
                        continue
                    if (lat := venue.get("latitude")) is None:
                        continue
                    if (long := venue.get("longitude")) is None:
                        continue
                    if (ticket_availability := event.get("ticket_availability")) is None:
                        continue

                    if not (eb_subcategory_id := event.get("subcategory_id")):
                        continue
                    if not (vivial_subcategory := get_vivial_subcategory_from_eventbrite_subcategory_id(eb_subcategory_id)):
                        continue

                    if not (eb_format_id := event.get("format_id")):
                        continue
                    if not (vivial_format := get_vivial_format_from_eventbrite_format_id(eb_format_id)):
                        continue

                    if (minimum_ticket_price := ticket_availability.get("minimum_ticket_price")) is not None:
                        min_cost_cents = minimum_ticket_price["value"]
                    else:
                        min_cost_cents = None

                    if (maximum_ticket_price := ticket_availability.get("maximum_ticket_price")) is not None:
                        max_cost_cents = maximum_ticket_price["value"]
                    else:
                        max_cost_cents = None

                    if event_start := event.get("start"):
                        start_time = datetime.fromisoformat(event_start["local"]).replace(tzinfo=ZoneInfo(event_start["timezone"]))
                    else:
                        start_time = None

                    if event_end := event.get("end"):
                        end_time = datetime.fromisoformat(event_end["local"]).replace(tzinfo=ZoneInfo(event_end["timezone"]))
                    else:
                        end_time = None

                    target = (await EventbriteEventOrm.query(session=db_session, params=EventbriteEventOrm.QueryParams(eventbrite_event_id=eventbrite_event_id))).one_or_none()
                    if not target:
                        target = EventbriteEventOrm(eventbrite_event_id=eventbrite_event_id)
                        db_session.add(target)

                    target.update(
                        title=event_name["text"],
                        start_time=start_time,
                        end_time=end_time,
                        min_cost_cents=min_cost_cents,
                        max_cost_cents=max_cost_cents,
                        coordinates=GeoCoordinates(lat=lat, long=long),
                        subcategory_id=vivial_subcategory.id,
                        format_id=vivial_format.id,
                    )

                    # if venue := event.get("venue"):
                    #     area_id = find_area_id(venue)
                    #     if area_id:
                    #         if address := venue.get("address"):
                    #             print(address.get("localized_address_display"), " ---> ", area_id.name)


# def find_area_id(venue: Venue) -> GeoArea | None:
#     address = venue.get("address")
#     if not address:
#         return None

#     event_lat = address.get("latitude")
#     event_lon = address.get("longitude")

#     if event_lat is None or event_lon is None:
#         return None

#     min_distance = math.inf
#     closest_area: GeoArea | None = None

#     for area in LOS_ANGELES_AREAS:
#         distance = haversine_distance(float(event_lat), float(event_lon), float(area.lat), float(area.lon))
#         if distance < min_distance:
#             min_distance = distance
#             closest_area = area

#     return closest_area
