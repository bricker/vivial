from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.booking import BookingDetailPeek, BookingDetails
from eave.core.graphql.types.pricing import CostBreakdown
from eave.core.lib.event_helpers import get_activity, get_restaurant
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.stdlib.http_exceptions import NotFoundError
from eave.stdlib.util import unwrap


async def _get_booking_details(
    booking: BookingOrm,
) -> BookingDetails:
    details = BookingDetails(
        id=booking.id,
        cost_breakdown=CostBreakdown(),
        headcount=0,
        activity=None,
        activity_start_time=None,
        restaurant=None,
        restaurant_arrival_time=None,
        driving_time=None,  # TODO: can we fill this in?
    )
    # NOTE: only getting 1 (or None) result here instead of full scalars result since
    # response type only accepts one of each
    activity_orm = None
    reservation_orm = None

    if len(booking.activities) > 0:
        activity_orm = booking.activities[0]
    if len(booking.reservations) > 0:
        reservation_orm = booking.reservations[0]

    if activity_orm:
        details.activity_start_time = activity_orm.start_time_local
        details.headcount = max(details.headcount, activity_orm.headcount)
        activity = await get_activity(
            source_id=activity_orm.source_id,
            source=activity_orm.source,
        )

        if activity:
            details.activity = activity
            if activity.ticket_info:
                details.cost_breakdown = activity.ticket_info.cost_breakdown

    if reservation_orm:
        details.restaurant_arrival_time = reservation_orm.start_time_local
        details.restaurant = await get_restaurant(
            source_id=reservation_orm.source_id,
            source=reservation_orm.source,
        )
        details.headcount = max(details.headcount, reservation_orm.headcount)

    return details


async def list_bookings_query(
    *,
    info: strawberry.Info[GraphQLContext],
) -> list[BookingDetailPeek]:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(db_session, account_id)

    booking_details = []

    for booking in account.bookings:
        # NOTE: only getting 1 (or None) result here instead of full scalars result since
        # response type only accepts one of each
        activity = None
        reservation = None

        if len(booking.activities) > 0:
            activity = booking.activities[0]

        if len(booking.reservations) > 0:
            reservation = booking.reservations[0]

        photo_uri = None
        if reservation and reservation.photo_uri:
            photo_uri = reservation.photo_uri
        if activity and activity.photo_uri:
            photo_uri = activity.photo_uri

        booking_details.append(
            BookingDetailPeek(
                id=booking.id,
                activity_start_time=activity.start_time_local if activity else None,
                activity_name=activity.name if activity else None,
                restaurant_name=reservation.name if reservation else None,
                restaurant_arrival_time=reservation.start_time_local if reservation else None,
                photo_uri=photo_uri,
            )
        )

    return booking_details


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

    # FIXME: This is inefficient, there is a better way to select just the right one using SQL.
    booking = next((b for b in account.bookings if b.id == input.booking_id), None)
    if not booking:
        raise NotFoundError("Booking not found")

    detail = await _get_booking_details(
        booking=booking,
    )

    return detail
