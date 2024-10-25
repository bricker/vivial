from eave.stdlib.exceptions import InvalidDataError
from eave.stdlib.logging import LOGGER
import strawberry
from uuid import UUID

from eave.core.graphql.types.reserver_details import (
    ReserverDetails,
    SubmitReserverDetailsError,
    SubmitReserverDetailsErrorCode,
    SubmitReserverDetailsResult,
    SubmitReserverDetailsSuccess,
)
from eave.core.internal import database
from eave.core.internal.orm.reserver_details import ReserverDetailsOrm


async def submit_reserver_details_mutation(
    *,
    info: strawberry.Info,
    account_id: UUID,  # TODO: need this here? or get auth from elsewhere?
    first_name: str,
    last_name: str,
    phone_number: str,
) -> SubmitReserverDetailsResult:
    try:
        async with database.async_session.begin() as db_session:
            reserver_details = await ReserverDetailsOrm.create(
                session=db_session,
                account_id=account_id,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
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
