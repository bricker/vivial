import uuid

import eave.stdlib.headers as eave_headers
from asgiref.typing import HTTPScope
from eave.stdlib import api_util, logger

from ..lib import request_state as request_util
from ..config import shared_config


def development_bypass_allowed(scope: HTTPScope) -> bool:
    if not shared_config.dev_mode:
        return False
    if shared_config.google_cloud_project == "eave-production":
        return False

    dev_header = api_util.get_header_value(scope=scope, name=eave_headers.EAVE_DEV_BYPASS_HEADER)
    if not dev_header:
        return False

    import os

    expected_uname = str(os.uname())
    if dev_header == expected_uname:
        logger.warning("Development bypass request accepted; some checks will be bypassed.")
        return True

    raise Exception()


async def development_bypass_auth(scope: HTTPScope) -> None:
    logger.warning("Bypassing auth verification in dev environment")
    eave_state = request_util.get_eave_state(scope=scope)
    account_id = api_util.get_header_value(scope=scope, name=eave_headers.EAVE_AUTHORIZATION_HEADER)
    if not account_id:
        raise Exception()

    eave_state.eave_account_id = uuid.UUID(account_id)
