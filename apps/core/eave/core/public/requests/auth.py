from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.stdlib import logger

from . import util as eave_request_util


async def get_access_token(input=eave_ops.GetAccessToken.RequestBody, request: fastapi.Request) -> eave_ops.GetAccessToken.ResponseBody:
    await eave_request_util.validate_signature_or_fail(request=request)
    session_token = request.cookies.get("ev_auth_session")
    assert session_token is not None

    async with eave_db.get_async_session() as db_session:
        account = await eave_orm.AccountOrm.one_or_exception()
        team = await eave_request_util.get_team_or_fail(session=db_session, request=request)

        subscription_orm = await eave_orm.SubscriptionOrm.one_or_exception(
            team_id=team.id,
            source=input.subscription.source,
            session=db_session,
        )

        document_reference_orm = await subscription_orm.get_document_reference(session=db_session)

    document_reference_public = (
        eave_models.DocumentReference.from_orm(document_reference_orm) if document_reference_orm is not None else None
    )

    return eave_ops.GetSubscription.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscription=eave_models.Subscription.from_orm(subscription_orm),
        document_reference=document_reference_public,
    )
