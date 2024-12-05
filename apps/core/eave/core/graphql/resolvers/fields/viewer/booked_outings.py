import copy
import datetime
from uuid import UUID
from eave.stdlib.eventbrite.client import EventbriteClient
from eave.stdlib.util import unwrap
import strawberry
from google.maps.places_v1 import PlacesAsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from eave.core import database
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.booking import BookingDetails
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
    OutingState,
)
from eave.core.lib.event_helpers import get_activity, get_restuarant
from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm
from eave.core.shared.enums import ActivitySource, RestaurantSource


@strawberry.input
class ListBookedOutingsInput:
    outing_state: OutingState


async def get_booking_details(
    booking_id: UUID,
) -> BookingDetails:
    places_client = PlacesAsyncClient()
    activities_client = EventbriteClient(api_key=CORE_API_APP_CONFIG.eventbrite_api_key)
    activities_query = BookingActivityTemplateOrm.select().where(BookingActivityTemplateOrm.booking_id == booking_id)
    reservations_query = BookingReservationTemplateOrm.select().where(
        BookingReservationTemplateOrm.booking_id == booking_id
    )

    async with database.async_session.begin() as session:
        # NOTE: only getting 1 (or None) result here instead of full scalars result since
        # response type only accepts one of each
        activity = await session.scalar(activities_query)
        reservation = await session.scalar(reservations_query)

    details = BookingDetails(
        id=booking_id,
        headcount=0,
        activity=None,
        activity_start_time=None,
        restaurant=None,
        restaurant_arrival_time=None,
        driving_time=None,  # TODO: can we fill this in?
    )

    if activity:
        details.activity_start_time = activity.activity_start_time
        details.activity = await get_activity(
            event_id=activity.source_id,
            event_source=ActivitySource[activity.source],
            places_client=places_client,
            activities_client=activities_client,
        )
        details.headcount = max(details.headcount, activity.headcount)

    if reservation:
        details.restaurant_arrival_time = reservation.reservation_start_time
        details.restaurant = await get_restuarant(
            event_id=reservation.source_id,
            event_source=RestaurantSource[reservation.source],
            places_client=places_client,
        )
        details.headcount = max(details.headcount, reservation.headcount)

    return details


async def list_booked_outings_query(
    *,
    info: strawberry.Info[GraphQLContext],
    input: ListBookedOutingsInput | None = None,
) -> list[BookingDetails]:
    """Fetch list of booked outings by account ID.
    PAST outings are outings that have already occured.
    FUTURE outings are upcoming outings.
    """
    query = BookingOrm.select().where(BookingOrm.account_id == unwrap(info.context.get("authenticated_account_id")))
    booking_details = []

    async with database.async_session.begin() as db_session:
        booking_orms = await db_session.scalars(query)

    for booking in booking_orms:
        detail = await get_booking_details(
            booking_id=booking.id,
        )
        booking_details.append(detail)

    if input:
        match input.outing_state:
            case OutingState.PAST:
                pass # TODO: filter? are these inputs even necessary? ask leilenah
            case OutingState.FUTURE:
                pass
            case _:
                pass

    return booking_details
