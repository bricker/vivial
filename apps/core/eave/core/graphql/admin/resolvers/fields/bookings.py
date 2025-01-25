from datetime import datetime
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.activity import Activity
from eave.core.graphql.types.booking import BookingDetailsPeek
from eave.core.graphql.types.reserver_details import ReserverDetails
from eave.core.graphql.types.restaurant import Restaurant
from eave.core.graphql.types.survey import Survey
from eave.core.lib.event_helpers import resolve_activity_details, resolve_restaurant_details
from eave.core.orm.account import AccountOrm
from eave.core.orm.booking import BookingOrm
from eave.core.shared.enums import ActivitySource, BookingState, RestaurantSource


async def admin_list_bookings_query(
    *,
    info: strawberry.Info[GraphQLContext],
    account_id: UUID,
) -> list[BookingDetailsPeek]:
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
            BookingDetailsPeek(
                id=booking.id,
                activity_start_time=activity.start_time_local if activity else None,
                activity_name=activity.name if activity else None,
                restaurant_name=reservation.name if reservation else None,
                restaurant_arrival_time=reservation.start_time_local if reservation else None,
                photo_uri=photo_uri,
                state=booking.state,
            )
        )

    return booking_details


@strawberry.type
class AdminBookingInfo:
    id: UUID
    accounts: list[Account]
    activity_start_time: datetime | None
    activity_name: str | None
    activity_booking_link: str | None
    activity_source: ActivitySource | None
    activity_source_id: str | None
    restaurant_arrival_time: datetime | None
    restaurant_name: str | None
    restaurant_booking_link: str | None
    restaurant_source: RestaurantSource | None
    restaurant_source_id: str | None
    state: BookingState
    reserver_details: ReserverDetails | None
    stripe_payment_id: str | None
    survey: Survey | None


async def admin_get_booking_info_query(
    *,
    info: strawberry.Info[GraphQLContext],
    booking_id: UUID,
) -> AdminBookingInfo:
    async with database.async_session.begin() as session:
        booking = await BookingOrm.get_one(session, booking_id)

    booking_info = AdminBookingInfo(
        id=booking.id,
        accounts=[Account.from_orm(account) for account in booking.accounts],
        activity_start_time=None,
        activity_name=None,
        activity_booking_link=None,
        activity_source=None,
        activity_source_id=None,
        restaurant_name=None,
        restaurant_arrival_time=None,
        restaurant_booking_link=None,
        restaurant_source=None,
        restaurant_source_id=None,
        state=booking.state,
        reserver_details=ReserverDetails.from_orm(booking.reserver_details) if booking.reserver_details else None,
        stripe_payment_id=booking.stripe_payment_intent_reference.stripe_payment_intent_id
        if booking.stripe_payment_intent_reference
        else None,
        survey=Survey.from_orm(booking.outing.survey) if booking.outing and booking.outing.survey else None,
    )

    if booking.activities:
        activity = booking.activities[0]
        booking_info.activity_start_time = activity.start_time_local
        booking_info.activity_name = activity.name
        booking_info.activity_booking_link = activity.external_booking_link
        booking_info.activity_source = activity.source
        booking_info.activity_source_id = activity.source_id

    if booking.reservations:
        reservation = booking.reservations[0]
        booking_info.restaurant_arrival_time = reservation.start_time_local
        booking_info.restaurant_name = reservation.name
        booking_info.restaurant_booking_link = reservation.external_booking_link
        booking_info.restaurant_source = reservation.source
        booking_info.restaurant_source_id = reservation.source_id

    return booking_info


async def admin_get_booking_activity_query(
    *,
    info: strawberry.Info[GraphQLContext],
    booking_id: UUID,
) -> Activity | None:
    async with database.async_session.begin() as session:
        booking = await BookingOrm.get_one(session, booking_id)

    activity = None
    if len(booking.activities) > 0:
        activity_orm = booking.activities[0]
        activity = await resolve_activity_details(
            source_id=activity_orm.source_id,
            source=activity_orm.source,
            survey=booking.outing.survey if booking.outing else None,
        )

    return activity


async def admin_get_booking_restaurant_query(
    *,
    info: strawberry.Info[GraphQLContext],
    booking_id: UUID,
) -> Restaurant | None:
    async with database.async_session.begin() as session:
        booking = await BookingOrm.get_one(session, booking_id)

    restaurant = None
    if len(booking.reservations) > 0:
        reservation_orm = booking.reservations[0]
        restaurant = await resolve_restaurant_details(
            source_id=reservation_orm.source_id,
            source=reservation_orm.source,
        )

    return restaurant
