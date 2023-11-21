from typing import Optional
from uuid import UUID, uuid4

import strawberry.federation as sb
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.graphql.types.subscriptions import DocumentReference, Subscription, SubscriptionInput
from eave.core.graphql.types.team import Team
import eave.core.internal.database as eave_db
from eave.core.internal.orm.document_reference import DocumentReferenceOrm
from eave.core.internal.orm.subscription import SubscriptionOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.analytics import log_event
from eave.stdlib.core_api.models.subscriptions import SubscriptionSource, SubscriptionSourceEvent, SubscriptionSourcePlatform
from eave.stdlib.exceptions import UnexpectedMissingValue

@sb.type
class DocumentSearchResult:
    title: str = sb.field()
    url: Optional[str] = sb.field()

@sb.input
class DocumentInput:
    title: str = sb.field()
    content: str = sb.field()
    parent: Optional["DocumentInput"] = sb.field()

@sb.type
class UpsertDocumentMutationResult(MutationResult):
    team: Team
    subscriptions: list[Subscription]
    document_reference: DocumentReference

class DocumentReferenceMutationResult(MutationResult):
    document_reference: DocumentReference

class DocumentResolvers:
    @staticmethod
    async def upsert_document(team_id: UUID, subscriptions: list[SubscriptionInput], document: DocumentInput) -> DocumentReferenceMutationResult:
        async with eave_db.async_session.begin() as db_session:
            eave_team = await TeamOrm.one_or_exception(
                session=db_session,
                team_id=team_id,
            )
            # get all subscriptions we wish to associate the new document with
            subscription_orms = [
                await SubscriptionOrm.one_or_exception(
                    team_id=eave_team.id,
                    source=SubscriptionSource(
                        platform=SubscriptionSourcePlatform(value=subscription.source.platform),
                        event=SubscriptionSourceEvent(value=subscription.source.event),
                        id=subscription.source.id,
                    ),
                    session=db_session,
                )
                for subscription in subscriptions
            ]

            # make sure we got even 1 subscription
            if len(subscriptions) < 1:
                raise UnexpectedMissingValue("Expected to have at least 1 subscription input")

            destination = await eave_team.get_document_client(session=db_session)
            if destination is None:
                # TODO: Error message: "You have not setup a document destination"
                raise UnexpectedMissingValue("document destination")

            # TODO: boldly assuming all subscriptions have the same value for document_reference_id
            existing_document_reference = await subscription_orms[0].get_document_reference(session=db_session)

            if existing_document_reference is None:
                document_metadata = await destination.create_document(input=input.document, ctx=ctx)

                await log_event(
                    event_name="eave_created_documentation",
                    event_description="Eave created some documentation",
                    event_source="upsert document endpoint",
                    eave_team=eave_team.analytics_model,
                    opaque_params={
                        "destination_platform": eave_team.document_platform.value
                        if eave_team.document_platform
                        else None,
                        "subscription_sources": [
                            {
                                "platform": subscription.source.platform.value,
                                "event": subscription.source.event.value,
                                "id": subscription.source.id,
                            }
                            for subscription in input.subscriptions
                        ],
                    },
                    ctx=ctx,
                )

                document_reference = await DocumentReferenceOrm.create(
                    session=db_session,
                    team_id=eave_team.id,
                    document_id=document_metadata.id,
                    document_url=document_metadata.url,
                )
            else:
                await destination.update_document(
                    input=input.document,
                    document_id=existing_document_reference.document_id,
                    ctx=ctx,
                )

                await log_event(
                    event_name="eave_updated_documentation",
                    event_description="Eave updated some existing documentation",
                    event_source="upsert document endpoint",
                    eave_team=eave_team.analytics_model,
                    opaque_params={
                        "destination_platform": eave_team.document_platform.value
                        if eave_team.document_platform
                        else None,
                        "subscription_sources": [
                            {
                                "platform": subscription.source.platform.value,
                                "event": subscription.source.event.value,
                                "id": subscription.source.id,
                            }
                            for subscription in input.subscriptions
                        ],
                    },
                    ctx=ctx,
                )

                document_reference = existing_document_reference

            # update all subscriptions without a document reference
            for subscription in subscription_orms:
                if subscription.document_reference_id is None:
                    subscription.document_reference_id = document_reference.id

    @staticmethod
    async def delete_document(team_id: UUID, id: UUID) -> MutationResult:

        async with eave_db.async_session.begin() as db_session:
            eave_team = await TeamOrm.one_or_exception(
                session=db_session, team_id=team_id
            )

            destination = await eave_team.get_document_client(session=db_session)
            if destination is None:
                raise UnexpectedMissingValue("document destination")

            document_reference = await DocumentReferenceOrm.one_or_exception(
                session=db_session,
                team_id=eave_team.id,
                id=input.document_reference.id,
            )
            await destination.delete_document(document_id=document_reference.document_id, ctx=eave_state.ctx)

            subscriptions = await SubscriptionOrm.query(
                session=db_session,
                team_id=eave_team.id,
                document_reference_id=document_reference.id,
            )

            for subscription in subscriptions:
                await db_session.delete(subscription)
            await db_session.flush()
            await db_session.delete(document_reference)

        await log_event(
            event_name="eave_delete_documentation",
            event_description="Eave deleted for documentation",
            event_source="delete document endpoint",
            eave_team=eave_team.analytics_model,
            opaque_params={
                "destination_platform": eave_team.document_platform.value if eave_team.document_platform else None,
                "document_id": str(document_reference.id),
            },
            ctx=eave_state.ctx,
        )

        return Response(status_code=http.HTTPStatus.OK)

    @staticmethod
    async def search_documents(team_id: UUID, query: str) -> list[DocumentSearchResult]:
        async with eave_db.async_session.begin() as db_session:
            eave_team = await TeamOrm.one_or_exception(
                session=db_session, team_id=team_id
            )

            destination = await eave_team.get_document_client(session=db_session)
            if destination is None:
                raise UnexpectedMissingValue("document destination")

        search_results = await destination.search_documents(query=input.query, ctx=eave_state.ctx)

        await log_event(
            event_name="eave_searched_documentation",
            event_description="Eave searched for documentation",
            event_source="search documents endpoint",
            eave_team=eave_team.analytics_model,
            opaque_params={
                "destination_platform": eave_team.document_platform.value if eave_team.document_platform else None,
                "search_query": input.query,
            },
            ctx=eave_state.ctx,
        )

        model = SearchDocumentsOp.ResponseBody(
            team=eave_team.api_model,
            documents=search_results,
        )

        return eave.stdlib.api_util.json_response(status_code=http.HTTPStatus.OK, model=model)