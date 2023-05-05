from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.core.internal.orm.document_reference import DocumentReferenceOrm
from eave.core.internal.orm.subscription import SubscriptionOrm

from . import util as request_util


async def upsert_document(
    input: eave_ops.UpsertDocument.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.UpsertDocument.ResponseBody:
    eave_state = request_util.get_eave_state(request=request)
    team = eave_state.eave_team

    async with eave_db.async_session.begin() as db_session:
        # get all subscriptions we wish to associate the new document with
        subscriptions = [ # TODO: need to include id for uniqueness when doc ref id is none
                    await SubscriptionOrm.one_or_none(
                        team_id=team.id,
                        document_reference_id=subscription.document_reference_id,
                        source=subscription.source, 
                        session=db_session,
                        id=subscription.id,
                    )
                    for subscription in input.subscriptions
                ]
        

        destination = await team.get_document_destination(session=db_session)
        assert destination is not None, "You have not setup a document destination"

        # get all referenced documents
        existing_document_references = [
            await subscription.get_document_reference(session=db_session)
            for subscription in subscriptions
            if subscription is not None
        ]

        if existing_document_reference is None:
            document_metadata = await destination.create_document(input=input.document)

            document_reference = await DocumentReferenceOrm.create(
                session=db_session,
                team_id=team.id,
                document_id=document_metadata.id,
                document_url=document_metadata.url,
            )
        else:
            await destination.update_document(
                input=input.document,
                document_id=existing_document_reference.document_id,
            )
            document_reference = existing_document_reference

        # update all subscriptions without a document reference
        # TODO: is commit necessary?
        # TODO: when there were multiple existing documents, we can't know which document to assign to new
        # subscriptions. We probably need to split the functionality of this operation to clarify
        for subscription in subscriptions:
            if subscription.document_reference_id is None:
                subscription.document_reference_id = document_reference.id

    response.status_code = HTTPStatus.ACCEPTED

    return eave_ops.UpsertDocument.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscriptions=eave_models.Subscription.from_orm(subscription),
        document_reference=eave_models.DocumentReference.from_orm(document_reference),
    )
