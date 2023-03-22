from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi

from . import util as eave_request_util


async def upsert_document(
    input: eave_ops.UpsertDocument.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.UpsertDocument.ResponseBody:
    await eave_request_util.validate_signature_or_fail(request=request)

    async with await eave_db.get_session() as session:
        team = await eave_request_util.get_team_or_fail(session=session, request=request)

        subscription = await eave_orm.SubscriptionOrm.one_or_exception(
            team_id=team.id, source=input.subscription.source, session=session
        )

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

    response.status_code = HTTPStatus.ACCEPTED

    return eave_ops.UpsertDocument.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscription=eave_models.Subscription.from_orm(subscription),
        document_reference=eave_models.DocumentReference.from_orm(document_reference),
    )
