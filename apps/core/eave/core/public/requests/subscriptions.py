from http import HTTPStatus

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal.database as eave_db
from eave.core.internal.orm.subscription import SubscriptionOrm

from .. import request_state as request_util
from ..http_endpoint import HTTPEndpoint


class GetSubscription(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_util.get_eave_state(request=request)
        body = await request.body()
        input = eave_ops.GetSubscription.RequestBody.parse_obj(body)
        team = eave_state.eave_team

        async with eave_db.async_session.begin() as db_session:
            subscription_orm = await SubscriptionOrm.one_or_exception(
                team_id=team.id,
                source=input.subscription.source,
                session=db_session,
            )

            document_reference_orm = await subscription_orm.get_document_reference(session=db_session)

        document_reference_public = (
            eave_models.DocumentReference.from_orm(document_reference_orm)
            if document_reference_orm is not None
            else None
        )

        return eave_api_util.json_response(
            eave_ops.GetSubscription.ResponseBody(
                team=eave_models.Team.from_orm(team),
                subscription=eave_models.Subscription.from_orm(subscription_orm),
                document_reference=document_reference_public,
            )
        )


class CreateSubscription(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_util.get_eave_state(request=request)
        body = await request.json()
        input = eave_ops.CreateSubscription.RequestBody.parse_obj(body)
        team = eave_state.eave_team

        async with eave_db.async_session.begin() as db_session:
            subscription_orm = await SubscriptionOrm.one_or_none(
                team_id=team.id, source=input.subscription.source, session=db_session
            )

            if subscription_orm is None:
                subscription_orm = SubscriptionOrm(
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
            eave_models.DocumentReference.from_orm(document_reference_orm)
            if document_reference_orm is not None
            else None
        )

        return eave_api_util.json_response(
            model=eave_ops.CreateSubscription.ResponseBody(
                team=eave_models.Team.from_orm(team),
                subscription=eave_models.Subscription.from_orm(subscription_orm),
                document_reference=document_reference_public,
            ),
            status_code=status_code,
        )


class DeleteSubscription(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_util.get_eave_state(request=request)
        body = await request.json()
        input = eave_ops.DeleteSubscription.RequestBody.parse_obj(body)
        team = eave_state.eave_team

        async with eave_db.async_session.begin() as db_session:
            subscription_orm = await SubscriptionOrm.one_or_none(
                team_id=team.id, source=input.subscription.source, session=db_session
            )

            if subscription_orm is not None:
                await db_session.delete(subscription_orm)

        return Response(status_code=HTTPStatus.OK)
