import enum
from typing import Optional
import uuid
from eave.stdlib.core_api.models import BaseResponseModel

from eave.stdlib.core_api.models import BaseInputModel

import pydantic


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
