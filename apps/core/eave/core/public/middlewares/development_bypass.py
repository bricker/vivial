import uuid

import eave.core.internal
import eave.stdlib
from asgiref.typing import HTTPScope

from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.logging import eaveLogger


async def development_bypass_auth(scope: HTTPScope, eave_state: EaveRequestState) -> None:
    eaveLogger.warning("Bypassing auth verification in dev environment")
    account_id = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.AUTHORIZATION_HEADER)
    if not account_id:
        raise Exception()

    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_account = await eave.core.internal.orm.AccountOrm.one_or_exception(
            session=db_session,
            id=uuid.UUID(account_id),
        )

    eave_state.eave_account_id = str(eave_account.id)
