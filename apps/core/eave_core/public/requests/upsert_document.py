from http import HTTPStatus
from http.client import HTTPException
import fastapi
import eave_stdlib.core_api.operations as eave_ops
import eave_stdlib.core_api.models as eave_models
import eave_core.internal.orm as eave_orm
import eave_core.internal.util
import eave_core.internal.database as eave_db

class UpsertDocument:
    @staticmethod
    async def handler(input: eave_ops.UpsertDocument.RequestBody, request: fastapi.Request, response: fastapi.Response) -> eave_ops.UpsertDocument.RequestBody:
        state = eave_core.internal.util.StateWrapper(request.state)
        if state.team_id is None:
            raise HTTPException(HTTPStatus.FORBIDDEN)

        async with eave_db.session_factory() as session:
            team = await eave_orm.TeamOrm.find_one(team_id=state.team_id, session=session)
            if team is None:
                raise HTTPException(HTTPStatus.FORBIDDEN)

            subscription = await eave_orm.SubscriptionOrm.find_one(
                team_id=team.id, source=input.subscription.source, session=session
            )
            if subscription is None:
                raise HTTPException(HTTPStatus.NOT_FOUND)

            destination = await team.get_document_destination(session=session)
            existing_document_reference = await subscription.get_document_reference(session=session)

            if existing_document_reference is None:
                document_reference = await destination.create_document(
                    document=input.document,
                    session=session,
                )

                await session.commit()
                subscription.document_reference_id = document_reference.id
                await session.commit()

            else:
                document_reference = await destination.update_document(
                    document=input.document,
                    document_reference=existing_document_reference,
                )

        # Eventually this endpoint will accept the input and push to the destination offline.
        response.status_code = HTTPStatus.ACCEPTED

        return eave_ops.UpsertDocument.ResponseBody(
            team=eave_models.Team.from_orm(team),
            subscription=eave_models.Subscription.from_orm(subscription),
            document_reference=eave_models.DocumentReference.from_orm(document_reference),
        )
