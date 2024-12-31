from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.activity import ActivityPlan
from eave.core.graphql.types.booking import BookingDetails, BookingDetailsPeek
from eave.core.graphql.types.restaurant import Reservation
from eave.core.lib.event_helpers import resolve_activity_details, resolve_restaurant_details
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingActivityTemplateOrm, BookingOrm, BookingReservationTemplateOrm
from eave.core.shared.enums import BookingState
from eave.stdlib.logging import LOGGER
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

        activity = await resolve_activity_details(
            source_id=activity_orm.source_id,
            source=activity_orm.source,
            survey=booking_orm.outing.survey if booking_orm.outing else None,
        )

        if activity:
            activity_plan = ActivityPlan(
                activity=activity,
                start_time=activity_orm.start_time_local,
                headcount=activity_orm.headcount,
            )

    if len(booking_orm.reservations) > 0:
        reservation_orm = booking_orm.reservations[0]
        restaurant = await resolve_restaurant_details(
            source_id=reservation_orm.source_id,
            source=reservation_orm.source,
        )

        if restaurant:
            reservation = Reservation(
                restaurant=restaurant,
                arrival_time=reservation_orm.start_time_local,
                headcount=reservation_orm.headcount,
            )

    return BookingDetails(
        id=booking_orm.id,
        state=booking_orm.state,
        survey=None,
        activity_plan=activity_plan,
        reservation=reservation,
    )


async def list_bookings_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> list[BookingDetailsPeek]:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(db_session, account_id)

    booking_peeks = []

    for booking in sorted(account.bookings, key=lambda booking: booking.start_time_utc):
        if not booking.state.is_visible:
            # Only show the user confirmed or booked bookings
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
            BookingDetailsPeek(
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
) -> BookingDetails | None:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as session:
        account = await AccountOrm.get_one(session, account_id)

    booking_orm = account.get_booking(booking_id=input.booking_id)
    if not booking_orm or not booking_orm.state.is_visible:
        LOGGER.warning("Booking not found or invalid state", {"bookingId": str(input.booking_id)})
        return None

    detail = await _get_booking_details(
        booking_orm=booking_orm,
    )

    return detail
