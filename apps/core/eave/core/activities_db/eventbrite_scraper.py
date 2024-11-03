import asyncio
import math
import os

from eave.stdlib.eventbrite.client import EventbriteClient, OrderBy
from eave.stdlib.eventbrite.models.event import Event, EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.venue import Venue
from eave.stdlib.geo import GeoCoordinates
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap

from eave.core.internal.orm.eventbrite_event import EventbriteEventOrm
from eave.core.outing.constants.areas import LOS_ANGELES_AREAS
from eave.core.outing.models.geo_area import GeoArea

import eave.core.internal.database

_EVENTBRITE_ALLOWED_FORMAT_IDS = [
    5, # Festival
    6, # Performance
    7, # Screening
    8, # Gala
    9, # Class
    11, # Party
    13, # Tournament
    14, # Game
    16, # Tour
    17, # Attraction
    100, # Other
]

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
    )

async def get_eventbrite_events() -> None:
    client = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])

    for organizer_id in _EVENTBRITE_ORGANIZER_IDS:
        events = await client.list_events_for_organizer(
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

        events = [event for event in events if not _exclude_event(event)]

        async with eave.core.internal.database.async_session.begin() as db_session:
            for event in events:
                eventbrite_event_id = unwrap(event["id"])

                event_name = unwrap(event.get("name"))
                venue = unwrap(event.get("venue"))
                lat = unwrap(venue.get("latitude"))
                long = unwrap(venue.get("longitude"))

                await EventbriteEventOrm.create(
                    session=db_session,
                    eventbrite_event_id=eventbrite_event_id,
                    name=event["name"]["text"],
                    time_range=time_range,
                    cost_cents_range=cost_cents_range,
                    coordinates=GeoCoordinates(lat=venue .get("latitude"), long=event.get("venue").get("longitude")),
                    category_id=category_id,
                    subcategory_id=subcategory_id,
                )

                if venue := event.get("venue"):
                    area_id = find_area_id(venue)
                    if area_id:
                        if address := venue.get("address"):
                            print(address.get("localized_address_display"), " ---> ", area_id.name)

                # store event deltas in database
                # print(events)


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
