import enum
from typing import Optional
import uuid

from pydantic import BaseModel
import strawberry
from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel

@strawberry.enum
class SubscriptionSourcePlatform(enum.StrEnum):
    slack = "slack"
    github = "github"
    jira = "jira"

@strawberry.enum
class SubscriptionSourceEvent(enum.StrEnum):
    slack_message = "slack_message"
    github_file_change = "github_file_change"
    jira_issue_comment = "jira_issue_comment"

@strawberry.type
class DocumentReference:
    id: uuid.UUID
    document_id: str
    document_url: str

@strawberry.type
class SubscriptionSource:
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str

@strawberry.type
class Subscription:
    id: uuid.UUID
    document_reference_id: Optional[uuid.UUID]
    source: SubscriptionSource

@strawberry.input
class DocumentReferenceInput:
    id: uuid.UUID

@strawberry.input
class SubscriptionInput:
    source: SubscriptionSource


@strawberry.type
class SubscriptionInfo:
    """
    A simple wrapper around Subscription and DocumentReference that can be used in place of
    GetSubscriptionRequest or CreateSubscriptionRequest (which are incompatible with each other)
    """

    subscription: Optional[Subscription]
    document_reference: Optional[DocumentReference]
