from http import HTTPStatus

import eave.stdlib.api_util
import eave.stdlib.util
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response
import eave.core.internal.orm.team
from eave.stdlib.core_api.models.subscriptions import DocumentReference, Subscription
from eave.stdlib.core_api.operations.subscriptions import (
    GetSubscriptionRequest,
    CreateSubscriptionRequest,
    DeleteSubscriptionRequest,
)
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.http_endpoint import HTTPEndpoint


async def get_subscription(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = GetSubscriptionRequest.RequestBody.parse_obj(body)

    async with eave.core.internal.database.async_session.begin() as db_session:
        team = await eave.core.internal.orm.TeamOrm.one_or_exception(
            session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
        )

        subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
            team_id=team.id,
            source=input.subscription.source,
            session=db_session,
        )

        # This endpoint is used to check for an existing subscription. If the resource isn't found, it's not a
        # client error and a 404 is inappropriate, instead we return nils.

    if subscription_orm:
        document_reference_orm = await subscription_orm.get_document_reference(session=db_session)
    else:
        document_reference_orm = None

    return eave.stdlib.api_util.json_response(
        GetSubscriptionRequest.ResponseBody(
            team=team.api_model,
            subscription=subscription_orm.api_model if subscription_orm else None,
            document_reference=document_reference_orm.api_model if document_reference_orm else None,
        )
    )


async def create_subscription(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = CreateSubscriptionRequest.RequestBody.parse_obj(body)

    async with eave.core.internal.database.async_session.begin() as db_session:
        team = await eave.core.internal.orm.TeamOrm.one_or_exception(
            session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
        )

        subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
            team_id=team.id, source=input.subscription.source, session=db_session
        )

        if subscription_orm is None:
            subscription_orm = eave.core.internal.orm.SubscriptionOrm(
                team_id=team.id,
                source=input.subscription.source,
                document_reference_id=input.document_reference.id if input.document_reference is not None else None,
            )

            db_session.add(subscription_orm)
            status_code = HTTPStatus.CREATED
        else:
            status_code = HTTPStatus.OK

        document_reference_orm = await subscription_orm.get_document_reference(session=db_session)

    document_reference_public = (
        DocumentReference.from_orm(document_reference_orm) if document_reference_orm is not None else None
    )

    return eave.stdlib.api_util.json_response(
        model=CreateSubscriptionRequest.ResponseBody(
            team=Team.from_orm(team),
            subscription=Subscription.from_orm(subscription_orm),
            document_reference=document_reference_public,
        ),
        status_code=status_code,
    )


async def delete_subscription(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = DeleteSubscriptionRequest.RequestBody.parse_obj(body)

    async with eave.core.internal.database.async_session.begin() as db_session:
        team = await eave.core.internal.orm.TeamOrm.one_or_exception(
            session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
        )

        subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
            team_id=team.id, source=input.subscription.source, session=db_session
        )

        if subscription_orm is not None:
            await db_session.delete(subscription_orm)

    return Response(status_code=HTTPStatus.OK)
