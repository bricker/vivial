import enum
from typing import Optional
import uuid

from pydantic import BaseModel
from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel


class SubscriptionSourcePlatform(enum.StrEnum):
    slack = "slack"
    github = "github"
    jira = "jira"


class SubscriptionSourceEvent(enum.StrEnum):
    slack_message = "slack_message"
    github_file_change = "github_file_change"
    jira_issue_comment = "jira_issue_comment"


class DocumentReference(BaseResponseModel):
    id: uuid.UUID
    document_id: str
    document_url: str


class SubscriptionSource(BaseResponseModel):
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str


class Subscription(BaseResponseModel):
    id: uuid.UUID
    document_reference_id: Optional[uuid.UUID]
    source: SubscriptionSource


class DocumentReferenceInput(BaseInputModel):
    id: uuid.UUID


class SubscriptionInput(BaseInputModel):
    source: SubscriptionSource


class SubscriptionInfo(BaseModel):
    """
    A simple wrapper around Subscription and DocumentReference that can be used in place of
    GetSubscriptionRequest or CreateSubscriptionRequest (which are incompatible with each other)
    """

    subscription: Optional[Subscription]
    document_reference: Optional[DocumentReference]
