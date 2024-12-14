import math
import uuid
from textwrap import dedent

from google.maps.places import PlacesAsyncClient

from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.types.activity import Activity, ActivityCategoryGroup, ActivityVenue
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.lib.eventbrite import get_eventbrite_activity
from eave.core.lib.geo import GeoPoint
from eave.core.lib.google_places import (
    get_google_places_activity,
    get_google_places_restaurant,
    google_maps_directions_url,
)
from eave.core.orm.activity import ActivityOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.search_region import SearchRegionOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.eventbrite.client import EventbriteClient


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
    category_group = ActivityCategoryGroupOrm.one_or_none(activity_category_group_id=details.activity_category_group_id)

    return Activity(
        source_id=event_id,
        source=ActivitySource.INTERNAL,
        name=details.title,
        description=details.description,
        venue=ActivityVenue(
            name=details.title,
            location=Location(
                coordinates=GeoPoint(
                    lat=lat,
                    lon=lon,
                ),
                formatted_address=formatted_address,
                directions_uri=google_maps_directions_url(formatted_address),
            ),
        ),
        photos=None,  # TODO
        ticket_info=None,  # TODO
        website_uri=details.booking_url,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
        category_group=ActivityCategoryGroup.from_orm(category_group) if category_group else None,
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


def get_closest_search_region_to_point(
    *,
    regions: list[SearchRegionOrm],
    point: GeoPoint,
) -> SearchRegionOrm | None:
    """
    From the input `regions`, return the one that is closest to `point`.
    Only returns `None` if `regions` is empty.
    """
    closest_region = None
    activity_curr_min_dist = math.inf
    for region in regions:
        # see if dist to `activity` from `region` is less than from current closest `activity_region`
        dist_from_region_center = point.haversine_distance(to_point=region.area.center)
        if dist_from_region_center < activity_curr_min_dist:
            activity_curr_min_dist = dist_from_region_center
            closest_region = region

    return closest_region
