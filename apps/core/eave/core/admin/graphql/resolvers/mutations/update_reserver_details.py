import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.admin.graphql.context import AdminGraphQLContext
from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
)
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.errors import ValidationError


@strawberry.input
class AdminUpdateReserverDetailsInput:
    id: UUID
    first_name: str
    last_name: str
    phone_number: str


@strawberry.type
class AdminUpdateReserverDetailsSuccess:
    reserver_details: ReserverDetails


@strawberry.enum
class AdminUpdateReserverDetailsFailureReason(enum.Enum):
    RESERVER_DETAILS_NOT_FOUND = enum.auto()
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class AdminUpdateReserverDetailsFailure:
    failure_reason: AdminUpdateReserverDetailsFailureReason
    validation_errors: list[ValidationError] | None = None


AdminUpdateReserverDetailsResult = Annotated[
    AdminUpdateReserverDetailsSuccess | AdminUpdateReserverDetailsFailure,
    strawberry.union("AdminUpdateReserverDetailsResult"),
]


async def admin_update_reserver_details_mutation(
    *,
    info: strawberry.Info[AdminGraphQLContext],
    input: AdminUpdateReserverDetailsInput,
) -> AdminUpdateReserverDetailsResult:
    try:
        async with database.async_session.begin() as db_session:
            lookup = ReserverDetailsOrm.select().where(ReserverDetailsOrm.id == input.id)
            reserver_details = await db_session.scalar(lookup)
            if not reserver_details:
                return AdminUpdateReserverDetailsFailure(
                    failure_reason=AdminUpdateReserverDetailsFailureReason.RESERVER_DETAILS_NOT_FOUND,
                )
            reserver_details.first_name = input.first_name
            reserver_details.last_name = input.last_name
            reserver_details.phone_number = input.phone_number

        return AdminUpdateReserverDetailsSuccess(
            reserver_details=ReserverDetails.from_orm(reserver_details),
        )

    except InvalidRecordError as e:
        return AdminUpdateReserverDetailsFailure(
            failure_reason=AdminUpdateReserverDetailsFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )
