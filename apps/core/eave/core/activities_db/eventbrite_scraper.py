import asyncio
import math
import os

from eave.stdlib.eventbrite.client import EventbriteClient, OrderBy
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.venue import Venue

from ..internal.outing.constants.areas import LOS_ANGELES_AREAS
from ..internal.outing.models.geo_area import GeoArea

EVENTBRITE_ALLOWED_FORMAT_IDS = [
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

async def get_eventbrite_events() -> None:
    client = EventbriteClient(api_key=os.environ["EVENTBRITE_API_KEY"])
    organizer_ids = ["46435628873"]

    for organizer_id in organizer_ids:
        events = await client.list_events_for_organizer(
            organizer_id=organizer_id,
            query={
                "order_by": OrderBy.start_asc,
                "status": EventStatus.live,
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

        for event in events:
            if venue := event.get("venue"):
                area_id = find_area_id(venue)
                if area_id:
                    if address := venue.get("address"):
                        print(address.get("localized_address_display"), " ---> ", area_id.name)

            # store event deltas in database
            # print(events)


def find_area_id(venue: Venue) -> GeoArea | None:
    address = venue.get("address")
    if not address:
        return None

    event_lat = address.get("latitude")
    event_lon = address.get("longitude")

    if event_lat is None or event_lon is None:
        return None

    min_distance = math.inf
    closest_area: GeoArea | None = None

    for area in LOS_ANGELES_AREAS:
        distance = haversine_distance(float(event_lat), float(event_lon), float(area.lat), float(area.lon))
        if distance < min_distance:
            min_distance = distance
            closest_area = area

    return closest_area


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """https://en.wikipedia.org/wiki/Haversine_formula"""

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers (mean value)
    r = 6371.0
    return c * r


if __name__ == "__main__":
    asyncio.run(get_eventbrite_events())
