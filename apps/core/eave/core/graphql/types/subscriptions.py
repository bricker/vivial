import enum
from typing import Optional
import uuid

from pydantic import BaseModel
import strawberry.federation as sb
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

@sb.input
class DocumentReferenceInput:
    id: uuid.UUID = sb.field()

@sb.input
class SubscriptionInput:
    source: SubscriptionSource = sb.field()

