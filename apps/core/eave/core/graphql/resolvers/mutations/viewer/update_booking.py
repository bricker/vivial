import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.booking import (
    Booking,
)
from eave.core.orm.account import AccountOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap


@strawberry.input
class UpdateBookingInput:
    booking_id: UUID
    reserver_details_id: UUID | None = strawberry.UNSET


@strawberry.type
class UpdateBookingSuccess:
    booking: Booking


@strawberry.enum
class UpdateBookingFailureReason(enum.Enum):
    BOOKING_NOT_FOUND = enum.auto()
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdateBookingFailure:
    failure_reason: UpdateBookingFailureReason
    validation_errors: list[ValidationError] | None = None


UpdateBookingResult = Annotated[UpdateBookingSuccess | UpdateBookingFailure, strawberry.union("UpdateBookingResult")]


async def update_booking_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: UpdateBookingInput,
) -> UpdateBookingResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    async with database.async_session.begin() as db_session:
        account = await AccountOrm.get_one(db_session, account_id)

        # It's important that when getting the booking, we use BOTH the account ID and booking ID.
        # Otherwise, it would be possible to confirm any booking, even ones you don't own.
        booking = account.get_booking(booking_id=input.booking_id)

        if not booking:
            return UpdateBookingFailure(failure_reason=UpdateBookingFailureReason.BOOKING_NOT_FOUND)

        if input.reserver_details_id:
            # It's also important that we make sure the given reserver details ID belongs to the viewer account.
            reserver_details = await ReserverDetailsOrm.get_one(
                db_session, account_id=account_id, uid=input.reserver_details_id
            )
            booking.reserver_details = reserver_details

    return UpdateBookingSuccess(
        booking=Booking.from_orm(booking),
    )
