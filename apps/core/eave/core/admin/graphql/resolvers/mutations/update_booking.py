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
from eave.core.lib.event_helpers import get_activity, get_restaurant
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
    new_activity = new_restaurant = strawberry.UNSET
    if (
        input.activity_source is not None
        and input.activity_source is not strawberry.UNSET
        and input.activity_source_id is not None
        and input.activity_source_id is not strawberry.UNSET
    ):
        new_activity = await get_activity(source=input.activity_source, source_id=input.activity_source_id)
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
        new_restaurant = await get_restaurant(source=input.restaurant_source, source_id=input.restaurant_source_id)
        if new_restaurant is None:
            return AdminUpdateBookingFailure(failure_reason=AdminUpdateBookingFailureReason.RESTAURANT_SOURCE_NOT_FOUND)
    elif input.restaurant_source is None and input.restaurant_source_id is None:
        new_restaurant = None

    try:
        async with database.async_session.begin() as db_session:
            booking = await BookingOrm.get_one(db_session, input.booking_id)

            if input.state is not None and input.state is not strawberry.UNSET:
                booking.state = input.state

            # NOTE: only updating the first entry since we currently only create 1 event of each type per outing
            if booking.activities:
                if input.activity_start_time_utc is not None and input.activity_start_time_utc is not strawberry.UNSET:
                    booking.activities[0].start_time_utc = input.activity_start_time_utc
                if input.activity_headcount is not None and input.activity_headcount is not strawberry.UNSET:
                    booking.activities[0].headcount = input.activity_headcount
                if new_activity is not None and new_activity is not strawberry.UNSET:
                    booking.activities[0].source = new_activity.source
                    booking.activities[0].source_id = new_activity.source_id
                    booking.activities[0].name = new_activity.name
                    booking.activities[0].external_booking_link = new_activity.website_uri
                    booking.activities[0].address = new_activity.venue.location.address.to_address()
                    booking.activities[0].coordinates = new_activity.venue.location.coordinates.geoalchemy_shape()
                    booking.activities[0].photo_uri = (
                        new_activity.photos.cover_photo.src if new_activity.photos.cover_photo else None
                    )
                # delete event from booking if None was explicitly passed as input
                if new_activity is None:
                    await db_session.delete(booking.activities[0])

            if booking.reservations:
                if (
                    input.restaurant_start_time_utc is not None
                    and input.restaurant_start_time_utc is not strawberry.UNSET
                ):
                    booking.reservations[0].start_time_utc = input.restaurant_start_time_utc
                if input.restaurant_headcount is not None and input.restaurant_headcount is not strawberry.UNSET:
                    booking.reservations[0].headcount = input.restaurant_headcount
                if new_restaurant is not None and new_restaurant is not strawberry.UNSET:
                    booking.reservations[0].source = new_restaurant.source
                    booking.reservations[0].source_id = new_restaurant.source_id
                    booking.reservations[0].name = new_restaurant.name
                    booking.reservations[0].external_booking_link = new_restaurant.website_uri
                    booking.reservations[0].address = new_restaurant.location.address.to_address()
                    booking.reservations[0].coordinates = new_restaurant.location.coordinates.geoalchemy_shape()
                    booking.reservations[0].photo_uri = (
                        new_restaurant.photos.cover_photo.src if new_restaurant.photos.cover_photo else None
                    )
                # delete event from booking if None was explicitly passed as input
                if new_restaurant is None:
                    await db_session.delete(booking.reservations[0])
    except InvalidRecordError as e:
        return AdminUpdateBookingFailure(
            failure_reason=AdminUpdateBookingFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )

    return AdminUpdateBookingSuccess(
        booking=Booking.from_orm(booking),
    )
