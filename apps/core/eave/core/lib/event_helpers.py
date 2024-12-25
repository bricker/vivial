import math
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
from eave.core.lib.eventbrite import EventbriteUtility
from eave.core.lib.google_places import GooglePlacesUtility
from eave.core.orm.activity_category import ActivityCategoryOrm
from eave.core.orm.activity_category_group import ActivityCategoryGroupOrm
from eave.core.orm.evergreen_activity import EvergreenActivityOrm, EvergreenActivityTicketTypeOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.shared.enums import ActivitySource, OutingBudget, RestaurantSource


async def get_internal_activity(*, event_id: str, survey: SurveyOrm | None) -> Activity | None:
    places = GooglePlacesUtility()

    async with database.async_session.begin() as db_session:
        activity_orm = await EvergreenActivityOrm.get_one(db_session, uid=uuid.UUID(event_id))
        images = activity_orm.images

    category_group = None

    if category := ActivityCategoryOrm.one_or_none(activity_category_id=activity_orm.activity_category_id):
        category_group = ActivityCategoryGroupOrm.one_or_none(
            activity_category_group_id=category.activity_category_group_id
        )

    directions_uri = await places.google_maps_directions_url(format_address(activity_orm.address, singleline=True))

    # Start with a price with all 0's
    most_expensive_eligible_price = CostBreakdown()
    most_expensive_eligible_ticket_type: EvergreenActivityTicketTypeOrm | None = None

    for ticket_type in activity_orm.ticket_types:
        cost_breakdown = CostBreakdown(
            base_cost_cents=ticket_type.base_cost_cents,
            fee_cents=ticket_type.service_fee_cents,
            tax_cents=0,  # We'll calculate this below
        )

        cost_breakdown.tax_cents = math.floor(cost_breakdown.calculate_total_cost_cents() * ticket_type.tax_percentage)

        total_cost_cents = cost_breakdown.calculate_total_cost_cents()
        max_budget = survey.budget if survey else OutingBudget.default()

        # If The total cost is <= the upper bound of the user's selected budget, then it is eligible.
        cost_is_lte_max_budget = (
            max_budget.upper_limit_cents is None or total_cost_cents <= max_budget.upper_limit_cents
        )

        if cost_is_lte_max_budget and total_cost_cents > most_expensive_eligible_price.calculate_total_cost_cents():
            most_expensive_eligible_price = cost_breakdown
            most_expensive_eligible_ticket_type = ticket_type

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
            name=most_expensive_eligible_ticket_type.title,
            notes=None,
            cost_breakdown=most_expensive_eligible_price,
        )
        if most_expensive_eligible_ticket_type
        else None,
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
            places = GooglePlacesUtility()
            activity = await places.get_google_places_activity(event_id=source_id)

        case ActivitySource.EVENTBRITE:
            eventbrite = EventbriteUtility()
            activity = await eventbrite.get_eventbrite_activity(event_id=source_id, survey=survey)

    return activity


async def resolve_restaurant_details(
    *,
    source: RestaurantSource,
    source_id: str,
) -> Restaurant:
    places = GooglePlacesUtility()

    match source:
        case RestaurantSource.GOOGLE_PLACES:
            restaurant = await places.get_google_places_restaurant(restaurant_id=source_id)
            return restaurant
