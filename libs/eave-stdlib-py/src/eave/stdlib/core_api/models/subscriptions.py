import enum
from typing import Optional
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
    id: pydantic.UUID4
    document_id: str
    document_url: str


class SubscriptionSource(BaseResponseModel):
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str


class Subscription(BaseResponseModel):
    id: pydantic.UUID4
    document_reference_id: Optional[pydantic.UUID4]
    source: SubscriptionSource


class DocumentReferenceInput(BaseInputModel):
    id: pydantic.UUID4


class SubscriptionInput(BaseInputModel):
    source: SubscriptionSource
