from http import HTTPStatus
import http

import eave.stdlib
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response


class GetSubscription(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.core.public.request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.GetSubscription.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )

            subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
                team_id=team.id,
                source=input.subscription.source,
                session=db_session,
            )

            if not subscription_orm:
                # This endpoint expects to return None frequently, as it's used to check for an existing subscription.
                # So we shouldn't log anything.
                return Response(status_code=http.HTTPStatus.NOT_FOUND)

            document_reference_orm = await subscription_orm.get_document_reference(session=db_session)

        document_reference_public = (
            eave.stdlib.core_api.models.DocumentReference.from_orm(document_reference_orm)
            if document_reference_orm is not None
            else None
        )

        return eave.stdlib.api_util.json_response(
            eave.stdlib.core_api.operations.GetSubscription.ResponseBody(
                team=eave.stdlib.core_api.models.Team.from_orm(team),
                subscription=eave.stdlib.core_api.models.Subscription.from_orm(subscription_orm),
                document_reference=document_reference_public,
            )
        )


class CreateSubscription(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.core.public.request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.CreateSubscription.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
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
            eave.stdlib.core_api.models.DocumentReference.from_orm(document_reference_orm)
            if document_reference_orm is not None
            else None
        )

        return eave.stdlib.api_util.json_response(
            model=eave.stdlib.core_api.operations.CreateSubscription.ResponseBody(
                team=eave.stdlib.core_api.models.Team.from_orm(team),
                subscription=eave.stdlib.core_api.models.Subscription.from_orm(subscription_orm),
                document_reference=document_reference_public,
            ),
            status_code=status_code,
        )


class DeleteSubscription(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.core.public.request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.DeleteSubscription.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )

            subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
                team_id=team.id, source=input.subscription.source, session=db_session
            )

            if subscription_orm is not None:
                await db_session.delete(subscription_orm)

        return Response(status_code=HTTPStatus.OK)
