from http import HTTPStatus
from eave.core.internal.orm.document_reference import DocumentReferenceOrm

import eave.core.internal.database as eave_db
from eave.core.internal.orm.subscription import SubscriptionOrm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi

from . import util as request_util


async def upsert_document(
    input: eave_ops.UpsertDocument.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.UpsertDocument.ResponseBody:
    eave_state = request_util.get_eave_state(request=request)
    team = eave_state.eave_team

    async with eave_db.async_session.begin() as db_session:
        subscription = await SubscriptionOrm.one_or_exception(
            team_id=team.id, source=input.subscription.source, session=db_session
        )

        destination = await team.get_document_destination(session=db_session)
        # TODO: Error message: "You have not setup a document destination"
        assert destination is not None

        existing_document_reference = await subscription.get_document_reference(session=db_session)

        if existing_document_reference is None:
            document_metadata = await destination.create_document(input=input.document)

            document_reference = await DocumentReferenceOrm.create(
                session=db_session,
                team_id=team.id,
                document_id=document_metadata.id,
                document_url=document_metadata.url,
            )

            subscription.document_reference_id = document_reference.id

        else:
            await destination.update_document(
                input=input.document,
                document_id=existing_document_reference.document_id,
            )
            document_reference = existing_document_reference

    response.status_code = HTTPStatus.ACCEPTED

    return eave_ops.UpsertDocument.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscription=eave_models.Subscription.from_orm(subscription),
        document_reference=eave_models.DocumentReference.from_orm(document_reference),
    )
