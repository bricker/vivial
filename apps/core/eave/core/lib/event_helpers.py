import urllib.parse
import uuid
from textwrap import dedent

from google.maps.places import PlacesAsyncClient


from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.eventbrite import get_eventbrite_activity
from eave.core.lib.google_places import get_google_places_activity, get_google_places_restaurant
from eave.core.orm.activity import ActivityOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.eventbrite.client import EventbriteClient, GetEventQuery
from eave.stdlib.eventbrite.models.expansions import Expansion

async def get_internal_activity(*, event_id: str) -> Activity | None:
    async with database.async_session.begin() as db_session:
        details = await ActivityOrm.get_one(
            session=db_session,
            id=uuid.UUID(event_id),
        )
    lat, lon = details.coordinates_to_lat_lon()
    formatted_address = dedent(f"""
        {details.address.address1} {details.address.address2}
        {details.address.city}, {details.address.state} {details.address.zip}
        """).strip()

    return Activity(
        source_id=event_id,
        source=ActivitySource.INTERNAL,
        name=details.title,
        description=details.description,
        venue=ActivityVenue(
            name=details.title,
            location=Location(
                latitude=lat,
                longitude=lon,
                formatted_address=formatted_address,
                directions_uri="",
            ),
        ),
        photos=None, # TODO
        ticket_info=None, # TODO
        website_uri=details.booking_url,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
    )

async def get_activity(
    event_source: ActivitySource,
    event_id: str,
) -> Activity | None:
    places_client = PlacesAsyncClient()
    eventbrite_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    match event_source:
        case ActivitySource.INTERNAL:
            activity = await get_internal_activity(event_id=event_id)
            return activity

        case ActivitySource.GOOGLE_PLACES:
            activity = await get_google_places_activity(places_client=places_client, event_id=event_id)
            return activity

        case ActivitySource.EVENTBRITE:
            activity = await get_eventbrite_activity(eventbrite_client=eventbrite_client, event_id=event_id)


async def get_restaurant(
    event_source: RestaurantSource,
    restaurant_id: str,
) -> Restaurant:
    places_client = PlacesAsyncClient()

    match event_source:
        case RestaurantSource.GOOGLE_PLACES:
            restaurant = await get_google_places_restaurant(places_client=places_client, restaurant_id=restaurant_id)
            return restaurant

def google_maps_directions_url(address: str) -> str:
    urlsafe_addr = urllib.parse.quote_plus(address)
    return f"https://www.google.com/maps/place/{urlsafe_addr}"
