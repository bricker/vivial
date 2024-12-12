import enum
from typing import Annotated
from uuid import UUID

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
)
from eave.core.orm.base import InvalidRecordError
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.shared.errors import ValidationError
from eave.stdlib.util import unwrap


@strawberry.input
class UpdateReserverDetailsAccountInput:
    # reserver_details data
    id: UUID
    first_name: str
    last_name: str
    phone_number: str
    # account data
    email: str


@strawberry.type
class UpdateReserverDetailsAccountSuccess:
    reserver_details: ReserverDetails
    account: Account


@strawberry.enum
class UpdateReserverDetailsAccountFailureReason(enum.Enum):
    VALIDATION_ERRORS = enum.auto()


@strawberry.type
class UpdateReserverDetailsAccountFailure:
    failure_reason: UpdateReserverDetailsAccountFailureReason
    validation_errors: list[ValidationError] | None = None


SubmitReserverDetailsResult = Annotated[
    UpdateReserverDetailsAccountSuccess | UpdateReserverDetailsAccountFailure,
    strawberry.union("UpdateReserverDetailsAccountResult"),
]


async def update_reserver_details_account_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: UpdateReserverDetailsAccountInput,
) -> SubmitReserverDetailsResult:
    account = unwrap(info.context.get("authenticated_account"))

    try:
        async with database.async_session.begin() as db_session:
            db_session.add(account)
            account.email = input.email

            lookup = (
                ReserverDetailsOrm.select()
                .where(ReserverDetailsOrm.account_id == account.id)
                .where(ReserverDetailsOrm.id == input.id)
            )
            reserver_details = (await db_session.scalars(lookup)).one()
            reserver_details.first_name = input.first_name
            reserver_details.last_name = input.last_name
            reserver_details.phone_number = input.phone_number
            # validate
            await reserver_details.save(db_session)

        return UpdateReserverDetailsAccountSuccess(
            reserver_details=ReserverDetails.from_orm(reserver_details),
            account=Account.from_orm(account),
        )

    except InvalidRecordError as e:
        return UpdateReserverDetailsAccountFailure(
            failure_reason=UpdateReserverDetailsAccountFailureReason.VALIDATION_ERRORS,
            validation_errors=e.validation_errors,
        )
