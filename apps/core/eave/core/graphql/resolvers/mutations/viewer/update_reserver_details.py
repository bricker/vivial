import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
)
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap


@strawberry.input
class UpdateReserverDetailsInput:
    id: UUID
    first_name: str
    last_name: str
    phone_number: str


@strawberry.type
class UpdateReserverDetailsSuccess:
    reserver_details: ReserverDetails


@strawberry.enum
class UpdateReserverDetailsFailureReason(enum.Enum):
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdateReserverDetailsFailure:
    failure_reason: UpdateReserverDetailsFailureReason
    validation_errors: list[ValidationError] | None = None


SubmitReserverDetailsResult = Annotated[
    UpdateReserverDetailsSuccess | UpdateReserverDetailsFailure,
    strawberry.union("UpdateReserverDetailsResult"),
]


async def update_reserver_details_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: UpdateReserverDetailsInput,
) -> SubmitReserverDetailsResult:
    account_id = unwrap(info.context.get("authenticated_account_id"))

    try:
        async with database.async_session.begin() as db_session:
            reserver_details = await ReserverDetailsOrm.get_one(db_session, account_id=account_id, uid=input.id)
            reserver_details.first_name = input.first_name
            reserver_details.last_name = input.last_name
            reserver_details.phone_number = input.phone_number

        return UpdateReserverDetailsSuccess(
            reserver_details=ReserverDetails.from_orm(reserver_details),
        )

    except InvalidRecordError as e:
        return UpdateReserverDetailsFailure(
            failure_reason=UpdateReserverDetailsFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )
