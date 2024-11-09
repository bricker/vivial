from uuid import UUID, uuid4

import strawberry

from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
    ReserverDetailsInput,
    SubmitReserverDetailsError,
    SubmitReserverDetailsErrorCode,
    SubmitReserverDetailsResult,
    SubmitReserverDetailsSuccess,
)
from eave.core.internal import database
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.stdlib.exceptions import InvalidDataError
from eave.stdlib.logging import LOGGER

MOCK_RESERVER_DETAILS = ReserverDetails(
    id=uuid4(),
    account_id=uuid4(),
    first_name="Lana",
    last_name="Nguyen",
    phone_number="(555) 555-5555",
)


async def submit_reserver_details_mutation(
    *,
    info: strawberry.Info,
    input: ReserverDetailsInput,
) -> SubmitReserverDetailsResult:
    """
    phone_number parameter must be digits only (with the exception of country code +) to pass validation
    e.g. "+11234567890" or "1234567890"
    """
    try:
        async with database.async_session.begin() as db_session:
            reserver_details = await ReserverDetailsOrm.create(
                session=db_session,
                account_id=input.account_id,
                first_name=input.first_name,
                last_name=input.last_name,
                phone_number=input.phone_number,
            )
    except InvalidDataError as e:
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


async def reserver_details_query(*, info: strawberry.Info, account_id: UUID) -> list[ReserverDetails]:
    # TODO: Fetch list of reserver details by account_id.
    return [MOCK_RESERVER_DETAILS]
