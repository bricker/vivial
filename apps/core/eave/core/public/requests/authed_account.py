from http import HTTPStatus
from typing import cast
from apps.core.eave.core.public.state import EaveRequestState

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.stdlib import logger

from . import util as eave_request_util


async def get_current_account(request: fastapi.Request) -> eave_ops.GetAccount.ResponseBody:
    logger.info("authed_account.get_current_account")
    state = EaveRequestState(request.state)
    assert state.eave_auth_token

    async with eave_db.get_async_session() as db_session:
        auth_token_orm = await eave_orm.AuthTokenOrm.one_or_exception(session=db_session, token=state.eave_auth_token)
        account = await eave_orm.AccountOrm.one_or_exception(session=db_session, id=auth_token_orm.account_id)
        team = await eave_orm.TeamOrm.one_or_exception(session=db_session, id=account.team_id)

    return eave_ops.GetSubscription.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscription=eave_models.Subscription.from_orm(subscription_orm),
        document_reference=document_reference_public,
    )
