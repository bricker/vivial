import enum
from typing import Annotated
from uuid import UUID

import strawberry


@strawberry.type
class ReserverDetails:
    id: UUID
    account_id: UUID
    first_name: str
    last_name: str
    phone_number: str


@strawberry.enum
class SubmitReserverDetailsErrorCode(enum.StrEnum):
    INVALID_PHONE_NUMBER = "INVALID_PHONE_NUMBER"


@strawberry.type
class SubmitReserverDetailsSuccess:
    reserver_details: ReserverDetails


@strawberry.type
class SubmitReserverDetailsError:
    error_code: SubmitReserverDetailsErrorCode


SubmitReserverDetailsResult = Annotated[
    SubmitReserverDetailsSuccess | SubmitReserverDetailsError, strawberry.union("SubmitReserverDetailsResult")
]
