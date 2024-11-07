import enum
from typing import Annotated
from uuid import UUID

import strawberry


@strawberry.type
class Booking:
    id: UUID
    reserver_details_id: UUID


@strawberry.input
class CreateBookingInput:
    account_id: UUID  # TODO: need this here? or get auth from elsewhere?
    outing_id: UUID
    reserver_details_id: UUID


@strawberry.enum
class CreateBookingErrorCode(enum.StrEnum):
    START_TIME_TOO_SOON = "START_TIME_TOO_SOON"
    START_TIME_TOO_LATE = "START_TIME_TOO_LATE"


@strawberry.type
class CreateBookingSuccess:
    booking: Booking


@strawberry.type
class CreateBookingError:
    error_code: CreateBookingErrorCode


CreateBookingResult = Annotated[CreateBookingSuccess | CreateBookingError, strawberry.union("CreateBookingResult")]
