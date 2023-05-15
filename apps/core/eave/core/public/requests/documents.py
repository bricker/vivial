import http

import eave.pubsub_schemas
import eave.stdlib
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.exceptions import UnexpectedMissingValue


class UpsertDocument(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.core.public.request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.UpsertDocument.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )
            subscription = await eave.core.internal.orm.SubscriptionOrm.one_or_exception(
                team_id=team.id, source=input.subscription.source, session=db_session
            )

            destination = await team.get_document_destination(session=db_session)
            if destination is None:
                # TODO: Error message: "You have not setup a document destination"
                raise UnexpectedMissingValue("document destination")

            existing_document_reference = await subscription.get_document_reference(session=db_session)

            if existing_document_reference is None:
                document_metadata = await destination.create_document(input=input.document)

                eave.stdlib.analytics.log_event(
                    event_name="eave_created_documentation",
                    event_description="Eave created some documentation",
                    event_source="core api",
                    eave_team_id=team.id,
                    opaque_params={
                        "destination_platform": team.document_platform.value if team.document_platform else None,
                        "subscription_source.platform": input.subscription.source.platform.value,
                        "subscription_source.event": input.subscription.source.event.value,
                        "subscription_source.id": input.subscription.source.id,
                    },
                )

                document_reference = await eave.core.internal.orm.DocumentReferenceOrm.create(
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

                eave.stdlib.analytics.log_event(
                    event_name="eave_updated_documentation",
                    event_description="Eave updated some existing documentation",
                    event_source="core api",
                    eave_team_id=team.id,
                    opaque_params={
                        "destination_platform": team.document_platform.value if team.document_platform else None,
                        "subscription_source.platform": input.subscription.source.platform.value,
                        "subscription_source.event": input.subscription.source.event.value,
                        "subscription_source.id": input.subscription.source.id,
                    },
                )

                document_reference = existing_document_reference

        model = eave.stdlib.core_api.operations.UpsertDocument.ResponseBody(
            team=eave.stdlib.core_api.models.Team.from_orm(team),
            subscription=eave.stdlib.core_api.models.Subscription.from_orm(subscription),
            document_reference=eave.stdlib.core_api.models.DocumentReference.from_orm(document_reference),
        )
        return eave.stdlib.api_util.json_response(status_code=http.HTTPStatus.ACCEPTED, model=model)
