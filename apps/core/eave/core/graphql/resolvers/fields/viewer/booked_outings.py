import copy
import datetime
from uuid import UUID
from eave.stdlib.util import unwrap
import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.fields.outing import MOCK_OUTING
from eave.core.graphql.types.activity import Activity, ActivityTicketInfo, ActivityVenue
from eave.core.graphql.types.booking import BookingDetails
from eave.core.graphql.types.location import Location
from eave.core.graphql.types.outing import (
    Outing,
    OutingState,
)
from eave.core.orm.booking import BookingOrm
from eave.core.orm.booking_activities_template import BookingActivityTemplateOrm
from eave.core.orm.booking_reservations_template import BookingReservationTemplateOrm


@strawberry.input
class ListBookedOutingsInput:
    outing_state: OutingState


async def get_booking_details(
    session: AsyncSession,
    booking_id: UUID,
) -> BookingDetails:
    activities_query = BookingActivityTemplateOrm.select().where(BookingActivityTemplateOrm.booking_id == booking_id)
    reservations_query = BookingReservationTemplateOrm.select().where(BookingReservationTemplateOrm.booking_id == booking_id)

    # NOTE: only getting 1 (or None) result here instead of full scalars result since
    # response type only accepts one of each
    activity = await session.scalar(activities_query)
    reservation = await session.scalar(reservations_query)

    details = BookingDetails(
        id=booking_id,
        headcount=2,
        activity=None,
        activity_start_time=None,
        restaurant=None,
        restaurant_arrival_time=None,
        driving_time=None,
    )

    # @next do i create a completely different return type from Outing since
    #  we dont need to display this much detail, or do i update the teamplate types to hold more shit?
    if activity:
        details.activity_start_time = activity.activity_start_time
        details.activity = Activity(
            id=activity.id,
            source=None, # TDOO
            name=activity.activity_name,
            description=activity.activity_name,
            venue=ActivityVenue(
                name="",
                location=Location(
                    directions_uri="",
                    latitude=1,
                    longitude=1,
                    formatted_address=""
                ),
            ),
            photos=None,
            ticket_info=ActivityTicketInfo(
                type="",
                notes="",
                cost=0,
                fee=0,
                tax=0,
            ),
            website_uri="",
            door_tips="",
            insider_tips="",
            parking_tips="",
        )

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
        results = await db_session.scalars(query)
        for booking in results:
            detail = await get_booking_details(
                session=db_session,
                booking_id=booking.id,
            )
            booking_details.append(detail)

    if input:
        match input.outing_state:
            case OutingState.PAST:
                pass
            case OutingState.FUTURE:
                pass
            case _:
                pass

    return booking_details
