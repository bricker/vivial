import uuid

from eave.core import database
from eave.core.graphql.types.activity import Activity, ActivityCategoryGroup, ActivityVenue
from eave.core.graphql.types.address import GraphQLAddress
from eave.core.graphql.types.cost_breakdown import CostBreakdown
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.photos import Photo, Photos
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.graphql.types.ticket_info import TicketInfo
from eave.core.lib.address import format_address
from eave.core.lib.eventbrite import get_eventbrite_activity
from eave.core.lib.google_places import (
    get_google_places_activity,
    get_google_places_restaurant,
    google_maps_directions_url,
)
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.evergreen_activity import EvergreenActivityOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource


async def get_internal_activity(*, event_id: str, survey: SurveyOrm | None) -> Activity | None:
    async with database.async_session.begin() as db_session:
        activity_orm = await EvergreenActivityOrm.get_one(db_session, uid=uuid.UUID(event_id))
        images = activity_orm.images

    category_group = None

    if category := ActivityCategoryOrm.one_or_none(activity_category_id=activity_orm.activity_category_id):
        category_group = ActivityCategoryGroupOrm.one_or_none(
            activity_category_group_id=category.activity_category_group_id
        )

    directions_uri = await google_maps_directions_url(format_address(activity_orm.address, singleline=True))

    return Activity(
        source_id=event_id,
        source=ActivitySource.INTERNAL,
        name=activity_orm.title,
        description=activity_orm.description,
        venue=ActivityVenue(
            name=activity_orm.title,
            location=Location(
                coordinates=activity_orm.coordinates_to_geopoint(),
                address=GraphQLAddress.from_address(activity_orm.address),
                directions_uri=directions_uri,
            ),
        ),
        photos=Photos(
            cover_photo=Photo.from_orm(images[0]) if len(images) > 0 else None,
            supplemental_photos=[Photo.from_orm(image) for image in images[1:]],
        ),
        ticket_info=TicketInfo(
            name="FIXME",
            notes="FIXME",
            cost_breakdown=CostBreakdown(),  # FIXME
        ),
        website_uri=activity_orm.booking_url,
        door_tips=None,
        insider_tips=None,
        parking_tips=None,
        primary_type_name=None,
        category_group=ActivityCategoryGroup.from_orm(category_group) if category_group else None,
    )


async def resolve_activity_details(
    *,
    source: ActivitySource,
    source_id: str,
    survey: SurveyOrm | None,
) -> Activity | None:
    match source:
        case ActivitySource.INTERNAL:
            activity = await get_internal_activity(event_id=source_id, survey=survey)

        case ActivitySource.GOOGLE_PLACES:
            activity = await get_google_places_activity(event_id=source_id)

        case ActivitySource.EVENTBRITE:
            activity = await get_eventbrite_activity(event_id=source_id, survey=survey)

    return activity


async def resolve_restaurant_details(
    *,
    source: RestaurantSource,
    source_id: str,
) -> Restaurant:
    match source:
        case RestaurantSource.GOOGLE_PLACES:
            restaurant = await get_google_places_restaurant(restaurant_id=source_id)
            return restaurant
