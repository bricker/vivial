import asyncio
import math
import os

from eave.stdlib.eventbrite.client import EventbriteClient, OrderBy
from eave.stdlib.eventbrite.models.event import EventStatus
from eave.stdlib.eventbrite.models.expansions import Expansion
from eave.stdlib.eventbrite.models.venue import Venue

from dataclasses import dataclass


@dataclass
class GeoArea:
    name: str
    key: str
    lat: float
    lon: float
    rad: float

LA_AREAS = [
    GeoArea(name="Central LA & Hollywood", key="us_ca_la_1", lat=34.065730, lon=-118.323769, rad=5.78),
    GeoArea(name="Downtown Los Angeles", key="us_ca_la_2", lat=34.046422, lon=-118.245325, rad=1.69),
    GeoArea(name="Pasadena, Glendale, & Northeast LA", key="us_ca_la_3", lat=34.160040, lon=-118.209821, rad=6.49),
    GeoArea(name="Westside", key="us_ca_la_4", lat=33.965090, lon=-118.557344, rad=10.55),
    GeoArea(name="South Bay", key="us_ca_la_5", lat=33.856750, lon=-118.354487, rad=9.70),
    GeoArea(name="San Gabriel Valley", key="us_ca_la_6", lat=34.116746, lon=-118.016725, rad=8.46),
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

    for area in LA_AREAS:
        distance = haversine_distance(float(event_lat), float(event_lon), area.lat, area.lon)
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
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers (mean value)
    r = 6371.0
    return c * r

if __name__ == "__main__":
    asyncio.run(get_eventbrite_events())
