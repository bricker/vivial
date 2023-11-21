import enum
from typing import Optional
import uuid

from pydantic import BaseModel
import strawberry.federation as sb
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.internal.orm.document_reference import DocumentReferenceOrm
from eave.core.internal.orm.subscription import SubscriptionOrm
from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel

@sb.enum
class SubscriptionSourcePlatform(enum.StrEnum):
    slack = "slack"
    github = "github"
    jira = "jira"

@sb.enum
class SubscriptionSourceEvent(enum.StrEnum):
    slack_message = "slack_message"
    github_file_change = "github_file_change"
    jira_issue_comment = "jira_issue_comment"

@sb.type
class DocumentReference:
    id: uuid.UUID = sb.field()
    document_id: str = sb.field()
    document_url: str = sb.field()

    @classmethod
    def from_orm(cls, orm: DocumentReferenceOrm) -> "DocumentReference":
        return DocumentReference(
            id=orm.id,
            document_id=orm.document_id,
            document_url=orm.document_url,
        )

@sb.type
class SubscriptionSource:
    platform: SubscriptionSourcePlatform = sb.field()
    event: SubscriptionSourceEvent = sb.field()
    id: str = sb.field()

@sb.type
class Subscription:
    id: uuid.UUID = sb.field()
    document_reference_id: Optional[uuid.UUID] = sb.field()
    source: SubscriptionSource = sb.field()

    @classmethod
    def from_orm(cls, orm: SubscriptionOrm) -> "Subscription":
        return Subscription(
            id=orm.id,
            document_reference_id=orm.document_reference_id,
            source=SubscriptionSource(
                platform=SubscriptionSourcePlatform(value=orm.source_platform),
                event=SubscriptionSourceEvent(value=orm.source_event),
                id=orm.source_id,
            ),
        )

@sb.type
class SubscriptionInfo:
    """
    A simple wrapper around Subscription and DocumentReference that can be used in place of
    GetSubscriptionRequest or CreateSubscriptionRequest (which are incompatible with each other)
    """

    subscription: Optional[Subscription] = sb.field()
    document_reference: Optional[DocumentReference] = sb.field()

@sb.type
class SubscriptionMutationResult(MutationResult):
    subscription: Subscription

@sb.input
class DocumentReferenceInput:
    id: uuid.UUID = sb.field()

@sb.input
class SubscriptionQueryInput:
    source: SubscriptionSource = sb.field()

@sb.input
class CreateSubscriptionInput:
    source: SubscriptionSource = sb.field()

@sb.input
class DeleteSubscriptionInput:
    source: SubscriptionSource = sb.field()

class SubscriptionResolvers:
    @staticmethod
    def get_subscription(team_id: uuid.UUID, query: SubscriptionQueryInput) -> Optional[Subscription]:
        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
            )

            subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
                team_id=team.id,
                source=input.subscription.source,
                session=db_session,
            )

            # This endpoint is used to check for an existing subscription. If the resource isn't found, it's not a
            # client error and a 404 is inappropriate, instead we return nils.

        if subscription_orm:
            document_reference_orm = await subscription_orm.get_document_reference(session=db_session)
        else:
            document_reference_orm = None

        return eave.stdlib.api_util.json_response(
            GetSubscriptionRequest.ResponseBody(
                team=team.api_model,
                subscription=subscription_orm.api_model if subscription_orm else None,
                document_reference=document_reference_orm.api_model if document_reference_orm else None,
            )
        )


    @staticmethod
    def create_subscription(team_id: uuid.UUID, input: CreateSubscriptionInput, document_reference: DocumentReferenceInput) -> SubscriptionMutationResult:
        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
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
            DocumentReference.from_orm(document_reference_orm) if document_reference_orm is not None else None
        )

        return eave.stdlib.api_util.json_response(
            model=CreateSubscriptionRequest.ResponseBody(
                team=Team.from_orm(team),
                subscription=Subscription.from_orm(subscription_orm),
                document_reference=document_reference_public,
            ),
            status_code=status_code,
        )

    @staticmethod
    def delete_subscription(team_id: uuid.UUID, input: DeleteSubscriptionInput) -> MutationResult:
        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.ctx.eave_team_id)
            )

            subscription_orm = await eave.core.internal.orm.SubscriptionOrm.one_or_none(
                team_id=team.id, source=input.subscription.source, session=db_session
            )

            if subscription_orm is not None:
                await db_session.delete(subscription_orm)

        return Response(status_code=HTTPStatus.OK)
