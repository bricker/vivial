from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.core_api
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
        subscriptions = [
            await SubscriptionOrm.one_or_exception(
                team_id=team.id,
                source=subscription.source,
                session=db_session,
            )
            for subscription in input.subscriptions
        ]

        # make sure we got even 1 subscription
        assert len(subscriptions) > 0, "Expected to have at least 1 subscription input"

        destination = await team.get_document_destination(session=db_session)
        assert destination is not None, "You have not setup a document destination"

        # TODO: boldly assuming all subscriptions have the same value for document_reference_id
        existing_document_reference = await subscriptions[0].get_document_reference(session=db_session)

        if existing_document_reference is None:
            document_metadata = await destination.create_document(input=input.document)

            eave.stdlib.analytics.log_event(
                event_name="eave_created_documentation",
                event_description="Eave created some documentation",
                event_source="core api",
                eave_team_id=team.id,
                opaque_params={
                    "destination_platform": team.document_platform.value if team.document_platform else None,
                    "subscription_sources": [
                        {
                            "platform": subscription.source.platform.value,
                            "event": subscription.source.event.value,
                            "id": subscription.source.id,
                        }
                        for subscription in input.subscriptions
                    ]
                },
            )

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

            eave.stdlib.analytics.log_event(
                event_name="eave_updated_documentation",
                event_description="Eave updated some existing documentation",
                event_source="core api",
                eave_team_id=team.id,
                opaque_params={
                    "destination_platform": team.document_platform.value if team.document_platform else None,
                    "subscription_sources": [
                        {
                            "platform": subscription.source.platform.value,
                            "event": subscription.source.event.value,
                            "id": subscription.source.id,
                        }
                        for subscription in input.subscriptions
                    ]
                },
            )

            document_reference = existing_document_reference

        # update all subscriptions without a document reference
        for subscription in subscriptions:
            if subscription.document_reference_id is None:
                subscription.document_reference_id = document_reference.id

    response.status_code = HTTPStatus.ACCEPTED

    return eave_ops.UpsertDocument.ResponseBody(
        team=eave_models.Team.from_orm(team),
        subscriptions=[eave_models.Subscription.from_orm(subscription) for subscription in subscriptions],
        document_reference=eave_models.DocumentReference.from_orm(document_reference),
    )
