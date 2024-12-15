import enum
from typing import Annotated

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
)
from eave.core.orm.account import AccountOrm
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap


@strawberry.input
class SubmitReserverDetailsInput:
    first_name: str
    last_name: str
    phone_number: str


@strawberry.type
class SubmitReserverDetailsSuccess:
    reserver_details: ReserverDetails


@strawberry.enum
class SubmitReserverDetailsFailureReason(enum.Enum):
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class SubmitReserverDetailsFailure:
    failure_reason: SubmitReserverDetailsFailureReason
    validation_errors: list[ValidationError] | None = None


SubmitReserverDetailsResult = Annotated[
    SubmitReserverDetailsSuccess | SubmitReserverDetailsFailure, strawberry.union("SubmitReserverDetailsResult")
]


async def submit_reserver_details_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: SubmitReserverDetailsInput,
) -> SubmitReserverDetailsResult:
    """
    phone_number parameter must be digits only (with the exception of country code +) to pass validation
    e.g. "+11234567890" or "1234567890"
    """
    account_id = unwrap(info.context.get("authenticated_account_id"))

    try:
        async with database.async_session.begin() as db_session:
            account = await AccountOrm.get_one(db_session, account_id)
            reserver_details = ReserverDetailsOrm(
                db_session,
                account=account,
                first_name=input.first_name,
                last_name=input.last_name,
                phone_number=input.phone_number,
            )

        return SubmitReserverDetailsSuccess(reserver_details=ReserverDetails.from_orm(reserver_details))

    except InvalidRecordError as e:
        return SubmitReserverDetailsFailure(
            failure_reason=SubmitReserverDetailsFailureReason.VALIDATION_ERRORS, validation_errors=e.validation_errors
        )
