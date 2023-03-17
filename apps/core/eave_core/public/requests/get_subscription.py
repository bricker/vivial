from http import HTTPStatus
from http.client import HTTPException
import fastapi
import eave_stdlib.core_api.operations as eave_ops
import eave_stdlib.core_api.models as eave_models
import eave_core.internal.orm as eave_orm
import eave_core.internal.util
import eave_core.internal.database as eave_db


class GetSubscription:
    @staticmethod
    async def handler(input: eave_ops.GetSubscription.RequestBody, request: fastapi.Request, response: fastapi.Response) -> eave_ops.GetSubscription.ResponseBody:
        state = eave_core.internal.util.StateWrapper(request.state)
        if state.team_id is None:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        async with eave_db.session_factory() as session:
            team = await eave_orm.TeamOrm.find_one(team_id=state.team_id, session=session)
            if team is None:
                raise HTTPException(HTTPStatus.FORBIDDEN)

            subscription_orm = await eave_orm.SubscriptionOrm.find_one(
                team_id=team.id,
                source=input.subscription.source,
                session=session,
            )
            if subscription_orm is None:
                raise HTTPException(HTTPStatus.NOT_FOUND)

            document_reference_orm = await subscription_orm.get_document_reference(session=session)

        document_reference_public = (
            eave_models.DocumentReference.from_orm(document_reference_orm) if document_reference_orm is not None else None
        )

        return eave_ops.GetSubscription.ResponseBody(
            team=eave_models.Team.from_orm(team),
            subscription=eave_models.Subscription.from_orm(subscription_orm),
            document_reference=document_reference_public,
        )

