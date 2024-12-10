import uuid
from textwrap import dedent

from google.maps.places import PlacesAsyncClient

from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.eventbrite import get_eventbrite_activity
from eave.core.lib.google_places import (
    get_google_places_activity,
    get_google_places_restaurant,
    google_maps_directions_url,
)
from eave.core.orm.activity import ActivityOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.eventbrite.client import EventbriteClient


async def get_internal_activity(*, event_id: str) -> Activity | None:
    async with database.async_session.begin() as db_session:
        query = ActivityOrm.select(
            uid=uuid.UUID(event_id),
        ).join(ActivityImageOrm, ActivityOrm.id == ActivityImageOrm.activity_id)

        images = await ActivityImageOrm.select(activity_id=activity.id)
    lat, lon = activity.coordinates_to_lat_lon()
    formatted_address = dedent(f"""
        {activity.address.address1} {activity.address.address2}
        {activity.address.city}, {activity.address.state} {activity.address.zip}
        """).strip()

    return Activity(
        source_id=event_id,
        source=ActivitySource.INTERNAL,
        name=activity.title,
        description=activity.description,
        venue=ActivityVenue(
            name=activity.title,
            location=Location(
                latitude=lat,
                longitude=lon,
                formatted_address=formatted_address,
                directions_uri=google_maps_directions_url(formatted_address),
            ),
        ),
        photos=None,  # TODO
        ticket_info=None,  # TODO
        website_uri=activity.booking_url,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
    )


async def get_activity(
    *,
    source: ActivitySource,
    source_id: str,
) -> Activity | None:
    places_client = PlacesAsyncClient()
    eventbrite_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)

    match source:
        case ActivitySource.INTERNAL:
            activity = await get_internal_activity(event_id=source_id)
            return activity

        case ActivitySource.GOOGLE_PLACES:
            activity = await get_google_places_activity(places_client=places_client, event_id=source_id)
            return activity

        case ActivitySource.EVENTBRITE:
            activity = await get_eventbrite_activity(eventbrite_client=eventbrite_client, event_id=source_id)


async def get_restaurant(
    *,
    source: RestaurantSource,
    source_id: str,
) -> Restaurant:
    places_client = PlacesAsyncClient()

    match source:
        case RestaurantSource.GOOGLE_PLACES:
            restaurant = await get_google_places_restaurant(places_client=places_client, restaurant_id=source_id)
            return restaurant
