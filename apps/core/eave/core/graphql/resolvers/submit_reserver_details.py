import enum
from typing import Annotated

import strawberry

from eave.core import database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
)
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.stdlib.exceptions import ValidationError
from eave.stdlib.logging import LOGGER
from eave.stdlib.util import unwrap


@strawberry.input
class ReserverDetailsInput:
    first_name: str
    last_name: str
    phone_number: str


@strawberry.enum
class SubmitReserverDetailsErrorCode(enum.Enum):
    INVALID_PHONE_NUMBER = enum.auto()


@strawberry.type
class SubmitReserverDetailsSuccess:
    reserver_details: ReserverDetails


@strawberry.type
class SubmitReserverDetailsError:
    error_code: SubmitReserverDetailsErrorCode


SubmitReserverDetailsResult = Annotated[
    SubmitReserverDetailsSuccess | SubmitReserverDetailsError, strawberry.union("SubmitReserverDetailsResult")
]


async def submit_reserver_details_mutation(
    *,
    info: strawberry.Info[GraphQLContext],
    input: ReserverDetailsInput,
) -> SubmitReserverDetailsResult:
    """
    phone_number parameter must be digits only (with the exception of country code +) to pass validation
    e.g. "+11234567890" or "1234567890"
    """
    account_id = unwrap(info.context.authenticated_account_id)
    try:
        async with database.async_session.begin() as db_session:
            reserver_details = await ReserverDetailsOrm.create(
                session=db_session,
                account_id=account_id,
                first_name=input.first_name,
                last_name=input.last_name,
                phone_number=input.phone_number,
            )
    except ValidationError as e:
        LOGGER.exception(e)
        return SubmitReserverDetailsError(error_code=SubmitReserverDetailsErrorCode(e.code))

    return SubmitReserverDetailsSuccess(
        reserver_details=ReserverDetails(
            id=reserver_details.id,
            account_id=reserver_details.account_id,
            first_name=reserver_details.first_name,
            last_name=reserver_details.last_name,
            phone_number=reserver_details.phone_number,
        )
    )
