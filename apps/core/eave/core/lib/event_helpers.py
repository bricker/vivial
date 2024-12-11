import uuid

from google.maps.places import PlacesAsyncClient

from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photo
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.eventbrite import get_eventbrite_activity
from eave.core.lib.google_places import (
    get_google_places_activity,
    get_google_places_restaurant,
    google_maps_directions_url,
)
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.image import ImageOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.eventbrite.client import EventbriteClient


async def get_internal_activity(*, event_id: str) -> Activity | None:
    async with database.async_session.begin() as db_session:
        activity = await ActivityOrm.get_one(db_session, uid=uuid.UUID(event_id))
        images = activity.images

        cover_photo = Photo.from_orm(images[0]) if len(images) > 0 else None
        supplemental_photos = [Photo.from_orm(image) for image in images[1:]]

    return Activity(
        source_id=event_id,
        source=ActivitySource.INTERNAL,
        name=activity.title,
        description=activity.description,
        venue=ActivityVenue(
            name=activity.title,
            location=Location(
                coordinates=activity.coordinates_to_geopoint(),
                address=activity.address,
                directions_uri=google_maps_directions_url(activity.address.formatted_singleline),
            ),
        ),
        cover_photo=cover_photo,
        supplemental_photos=supplemental_photos,
        pricing=None, # FIXME
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
