import uuid
import eave.core.public.requests.util as request_util
import eave.stdlib.headers as eave_headers
import eave.core.internal.database as eave_db
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.config import app_config
from eave.stdlib import logger

from . import asgi_types

def development_bypass_allowed(scope: asgi_types.HTTPScope) -> bool:
    if not app_config.dev_mode:
        return False
    if app_config.google_cloud_project == "eave-production":
        return False

    dev_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_DEV_BYPASS_HEADER)
    if not dev_header:
        return False

    import os

    expected_uname = str(os.uname())
    if dev_header == expected_uname:
        logger.warning("Development bypass request accepted; some checks will be bypassed.")
        return True

    raise Exception()

async def development_bypass_auth(scope: asgi_types.HTTPScope) -> None:
    logger.warning("Bypassing auth verification in dev environment")
    eave_state = request_util.get_eave_state(scope=scope)
    account_id = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_AUTHORIZATION_HEADER)
    if not account_id:
        raise Exception()

    async with eave_db.async_session.begin() as db_session:
        account = await AccountOrm.one_or_exception(
            session=db_session,
            id=uuid.UUID(account_id),
        )

    eave_state.eave_account = account
