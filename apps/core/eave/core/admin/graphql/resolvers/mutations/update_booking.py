import enum
from datetime import datetime
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.admin.graphql.context import AdminGraphQLContext
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.lib.event_helpers import resolve_activity_details, resolve_restaurant_details
from eave.core.mail import send_booking_status_email
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.booking import BookingOrm
from eave.core.shared.enums import ActivitySource, BookingState, RestaurantSource
from eave.core.shared.errors import ValidationError


@strawberry.input
class AdminUpdateBookingInput:
    booking_id: UUID
    activity_start_time_utc: datetime | None = strawberry.UNSET
    activity_source: ActivitySource | None = strawberry.UNSET
    activity_source_id: str | None = strawberry.UNSET
    activity_headcount: int | None = strawberry.UNSET
    restaurant_start_time_utc: datetime | None = strawberry.UNSET
    restaurant_source: RestaurantSource | None = strawberry.UNSET
    restaurant_source_id: str | None = strawberry.UNSET
    restaurant_headcount: int | None = strawberry.UNSET
    state: BookingState | None = strawberry.UNSET


@strawberry.type
class AdminUpdateBookingSuccess:
    booking: Booking


@strawberry.enum
class AdminUpdateBookingFailureReason(enum.Enum):
    BOOKING_NOT_FOUND = enum.auto()
    VALIDATION_ERRORS = enum.auto()
    ACTIVITY_SOURCE_NOT_FOUND = enum.auto()
    RESTAURANT_SOURCE_NOT_FOUND = enum.auto()


@strawberry.type
class AdminUpdateBookingFailure:
    failure_reason: AdminUpdateBookingFailureReason
    validation_errors: list[ValidationError] | None = None


AdminUpdateBookingResult = Annotated[
    AdminUpdateBookingSuccess | AdminUpdateBookingFailure, strawberry.union("AdminUpdateBookingResult")
]


async def admin_update_booking_mutation(
    *,
    info: strawberry.Info[AdminGraphQLContext],
    input: AdminUpdateBookingInput,
) -> AdminUpdateBookingResult:
    """
    `None` inputs for *_source and *_source_id will trigger deletion of the activity or
    restaurant from the booking.
    """
    # fetch new activity/restaurnt to set, if any
    new_activity = strawberry.UNSET
    new_restaurant = strawberry.UNSET

    async with database.async_session.begin() as db_session:
        # Get the original booking so we can tell what changed.
        # There is a better way to do this using `db_session`
        # Note that this has to be in its own session
        original_booking = await BookingOrm.get_one(db_session, input.booking_id)

    async with database.async_session.begin() as db_session:
        updated_booking = await BookingOrm.get_one(db_session, input.booking_id)
        accounts = updated_booking.accounts

    if (
        input.activity_source is not None
        and input.activity_source is not strawberry.UNSET
        and input.activity_source_id is not None
        and input.activity_source_id is not strawberry.UNSET
    ):
        new_activity = await resolve_activity_details(
            source=input.activity_source,
            source_id=input.activity_source_id,
            survey=updated_booking.outing.survey if updated_booking.outing else None,
        )
        if new_activity is None:
            return AdminUpdateBookingFailure(failure_reason=AdminUpdateBookingFailureReason.ACTIVITY_SOURCE_NOT_FOUND)
    elif input.activity_source is None and input.activity_source_id is None:
        new_activity = None
    if (
        input.restaurant_source is not None
        and input.restaurant_source is not strawberry.UNSET
        and input.restaurant_source_id is not None
        and input.restaurant_source_id is not strawberry.UNSET
    ):
        new_restaurant = await resolve_restaurant_details(
            source=input.restaurant_source, source_id=input.restaurant_source_id
        )
        if new_restaurant is None:
            return AdminUpdateBookingFailure(failure_reason=AdminUpdateBookingFailureReason.RESTAURANT_SOURCE_NOT_FOUND)
    elif input.restaurant_source is None and input.restaurant_source_id is None:
        new_restaurant = None

    try:
        async with database.async_session.begin() as db_session:
            db_session.add(updated_booking)

            if input.state is not None and input.state is not strawberry.UNSET:
                updated_booking.state = input.state

            # NOTE: only updating the first entry since we currently only create 1 event of each type per outing
            if updated_booking.activities:
                if input.activity_start_time_utc is not None and input.activity_start_time_utc is not strawberry.UNSET:
                    updated_booking.activities[0].start_time_utc = input.activity_start_time_utc
                if input.activity_headcount is not None and input.activity_headcount is not strawberry.UNSET:
                    updated_booking.activities[0].headcount = input.activity_headcount
                if new_activity is not None and new_activity is not strawberry.UNSET:
                    updated_booking.activities[0].source = new_activity.source
                    updated_booking.activities[0].source_id = new_activity.source_id
                    updated_booking.activities[0].name = new_activity.name
                    updated_booking.activities[0].external_booking_link = new_activity.website_uri
                    updated_booking.activities[0].address = new_activity.venue.location.address.to_address()
                    updated_booking.activities[
                        0
                    ].coordinates = new_activity.venue.location.coordinates.geoalchemy_shape()
                    updated_booking.activities[0].photo_uri = (
                        new_activity.photos.cover_photo.src if new_activity.photos.cover_photo else None
                    )
                # delete event from booking if None was explicitly passed as input
                if new_activity is None:
                    await db_session.delete(updated_booking.activities[0])

            if updated_booking.reservations:
                if (
                    input.restaurant_start_time_utc is not None
                    and input.restaurant_start_time_utc is not strawberry.UNSET
                ):
                    updated_booking.reservations[0].start_time_utc = input.restaurant_start_time_utc
                if input.restaurant_headcount is not None and input.restaurant_headcount is not strawberry.UNSET:
                    updated_booking.reservations[0].headcount = input.restaurant_headcount
                if new_restaurant is not None and new_restaurant is not strawberry.UNSET:
                    updated_booking.reservations[0].source = new_restaurant.source
                    updated_booking.reservations[0].source_id = new_restaurant.source_id
                    updated_booking.reservations[0].name = new_restaurant.name
                    updated_booking.reservations[0].external_booking_link = new_restaurant.website_uri
                    updated_booking.reservations[0].address = new_restaurant.location.address.to_address()
                    updated_booking.reservations[0].coordinates = new_restaurant.location.coordinates.geoalchemy_shape()
                    updated_booking.reservations[0].photo_uri = (
                        new_restaurant.photos.cover_photo.src if new_restaurant.photos.cover_photo else None
                    )
                # delete event from booking if None was explicitly passed as input
                if new_restaurant is None:
                    await db_session.delete(updated_booking.reservations[0])
    except InvalidRecordError as e:
        return AdminUpdateBookingFailure(
            failure_reason=AdminUpdateBookingFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )

    if original_booking.state != BookingState.BOOKED and updated_booking.state == BookingState.BOOKED:
        send_booking_status_email(
            booking_orm=updated_booking,
            emails=[a.email for a in accounts]
        )

    return AdminUpdateBookingSuccess(
        booking=Booking.from_orm(updated_booking),
    )
