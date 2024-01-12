import uuid
import aiohttp

import eave.core.internal
from eave.core.internal.orm.account import AccountOrm
import eave.stdlib.api_util
from asgiref.typing import HTTPScope

from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.logging import eaveLogger


async def development_bypass_auth(scope: HTTPScope) -> None:
    eave_state = EaveRequestState.load(scope=scope)
    eaveLogger.warning("Bypassing auth verification in dev environment", eave_state.ctx)
    account_id = eave.stdlib.api_util.get_header_value(scope=scope, name=aiohttp.hdrs.AUTHORIZATION)
    if not account_id:
        raise Exception()

    async with eave.core.internal.database.async_session.begin() as db_session:
        eave_account = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(
                id=uuid.UUID(account_id),
            ),
        )

    eave_state.ctx.eave_account_id = str(eave_account.id)
