import http

import eave.pubsub_schemas
import eave.stdlib
import eave.core.internal
import eave.core.public
import eave.stdlib.request_state
from starlette.requests import Request
from starlette.responses import Response
from eave.core.internal.orm.team import TeamOrm

import eave.core.internal.database as eave_db
from eave.stdlib.exceptions import UnexpectedMissingValue
import eave.stdlib.request_state as request_state
from eave.core.internal.orm.subscription import SubscriptionOrm
import eave.stdlib.api_util


class UpsertDocument(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = request_state.get_eave_state(request=request)
        # FIXME: Use the parsed body already at `eave_state.parsed_request_body`
        body = await request.json()
        input = eave.stdlib.core_api.operations.UpsertDocument.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            team = await TeamOrm.one_or_exception(
                session=db_session,
                team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id),
            )
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
            if len(subscriptions) < 1:
                raise UnexpectedMissingValue("Expected to have at least 1 subscription input")

            destination = await team.get_document_destination(session=db_session)
            if destination is None:
                # TODO: Error message: "You have not setup a document destination"
                raise UnexpectedMissingValue("document destination")

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
                        ],
                    },
                )

                document_reference = await eave.core.internal.orm.DocumentReferenceOrm.create(
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
                        ],
                    },
                )

                document_reference = existing_document_reference

            # update all subscriptions without a document reference
            for subscription in subscriptions:
                if subscription.document_reference_id is None:
                    subscription.document_reference_id = document_reference.id

        model = eave.stdlib.core_api.operations.UpsertDocument.ResponseBody(
            team=team.api_model,
            subscriptions=[subscription.api_model for subscription in subscriptions],
            document_reference=document_reference.api_model,
        )

        return eave.stdlib.api_util.json_response(status_code=http.HTTPStatus.ACCEPTED, model=model)


class SearchDocuments(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.stdlib.request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.SearchDocuments.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )

            destination = await eave_team.get_document_destination(session=db_session)
            if destination is None:
                raise UnexpectedMissingValue("document destination")

        search_results = await destination.search_documents(query=input.query)
        model = eave.stdlib.core_api.operations.SearchDocuments.ResponseBody(
            team=eave_team.api_model,
            documents=search_results,
        )

        return eave.stdlib.api_util.json_response(status_code=http.HTTPStatus.OK, model=model)


class DeleteDocument(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.stdlib.request_state.get_eave_state(request=request)
        body = await request.json()
        input = eave.stdlib.core_api.operations.DeleteDocument.RequestBody.parse_obj(body)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )

            destination = await eave_team.get_document_destination(session=db_session)
            if destination is None:
                raise UnexpectedMissingValue("document destination")

            document_reference = await eave.core.internal.orm.DocumentReferenceOrm.one_or_exception(
                session=db_session,
                team_id=eave_team.id,
                id=input.document_reference.id,
            )
            await destination.delete_document(document_id=document_reference.document_id)
            await db_session.delete(document_reference)

        return Response(status_code=http.HTTPStatus.OK)
