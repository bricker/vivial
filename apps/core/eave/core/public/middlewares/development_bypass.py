import uuid

import eave.stdlib
import eave.core.internal
import eave.core.public
from asgiref.typing import HTTPScope

from eave.stdlib.logging import eaveLogger


def development_bypass_allowed(scope: HTTPScope) -> bool:
    if not eave.core.internal.app_config.dev_mode:
        return False
    if eave.core.internal.app_config.google_cloud_project == "eave-production":
        return False

    dev_header = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.EAVE_DEV_BYPASS_HEADER)
    if not dev_header:
        return False

    import os

    expected_uname = str(os.uname())
    if dev_header == expected_uname:
        eaveLogger.warning("Development bypass request accepted; some checks will be bypassed.")
        return True

    raise Exception()


async def development_bypass_auth(
    scope: HTTPScope, eave_state: eave.core.public.request_state.EaveRequestState
) -> None:
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
