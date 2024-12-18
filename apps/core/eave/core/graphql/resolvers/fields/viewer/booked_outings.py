from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityPlan
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.graphql.types.restaurant import Reservation
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.shared.enums import BookingState
from eave.stdlib.http_exceptions import NotFoundError
from eave.stdlib.util import unwrap


async def _get_booking_details(
    booking_orm: BookingOrm,
) -> BookingDetails:
    # NOTE: only getting 1 (or None) result here instead of full scalars result since
    # response type only accepts one of each

    activity_plan: ActivityPlan | None = None
    reservation: Reservation | None = None

    if len(booking_orm.activities) > 0:
        activity_orm = booking_orm.activities[0]

        activity = await get_activity(
            source_id=activity_orm.source_id,
            source=activity_orm.source,
        )

        if activity:
            activity_plan = ActivityPlan(
                activity=activity,
                start_time=activity_orm.start_time_local,
                headcount=activity_orm.headcount,
            )

    if len(booking_orm.reservations) > 0:
        reservation_orm = booking_orm.reservations[0]
        restaurant = await get_restaurant(
            source_id=reservation_orm.source_id,
            source=reservation_orm.source,
        )

        reservation = Reservation(
            restaurant=restaurant,
            arrival_time=reservation_orm.start_time_local,
            headcount=reservation_orm.headcount,
        )

    return BookingDetails(
        id=booking_orm.id,
        state=booking_orm.state,
        activity_plan=activity_plan,
        reservation=reservation,
    )


async def list_bookings_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> list[BookingDetailPeek]:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(db_session, account_id)

    booking_peeks = []

    for booking in account.bookings:
        if booking.state != BookingState.CONFIRMED:
            continue

        # NOTE: only getting 1 (or None) result here instead of full scalars result since
        # response type only accepts one of each
        activity_orm: BookingActivityTemplateOrm | None = None
        reservation_orm: BookingReservationTemplateOrm | None = None

        if len(booking.activities) > 0:
            activity_orm = booking.activities[0]

        if len(booking.reservations) > 0:
            reservation_orm = booking.reservations[0]

        if activity_orm and activity_orm.photo_uri:
            photo_uri = activity_orm.photo_uri
        elif reservation_orm and reservation_orm.photo_uri:
            photo_uri = reservation_orm.photo_uri
        else:
            photo_uri = None

        booking_peeks.append(
            BookingDetailPeek(
                id=booking.id,
                activity_start_time=activity_orm.start_time_local if activity_orm else None,
                activity_name=activity_orm.name if activity_orm else None,
                restaurant_name=reservation_orm.name if reservation_orm else None,
                restaurant_arrival_time=reservation_orm.start_time_local if reservation_orm else None,
                photo_uri=photo_uri,
                state=booking.state,
            )
        )

    return booking_peeks


@strawberry.input
class GetBookingDetailsQueryInput:
    booking_id: UUID


async def get_booking_details_query(
    *,
    info: strawberry.Info[GraphQLContext],
    input: GetBookingDetailsQueryInput,
) -> BookingDetails:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as session:
        account = await AccountOrm.get_one(session, account_id)

    booking_orm = account.get_booking(booking_id=input.booking_id)
    if not booking_orm:
        raise NotFoundError("Booking not found")

    detail = await _get_booking_details(
        booking_orm=booking_orm,
    )

    return detail
