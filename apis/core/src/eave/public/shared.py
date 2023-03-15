import enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentPlatform(str, enum.Enum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"

class SubscriptionSourcePlatform(str, enum.Enum):
    slack = "slack"
    github = "github"
    jira = "jira"


class SubscriptionSourceEvent(str, enum.Enum):
    slack_message = "slack_message"
    github_file_change = "github_file_change"
    jira_issue_comment = "jira_issue_comment"

class DocumentContentInput(BaseModel):
    title: str
    content: str
    parent: Optional["DocumentContentInput"] = None


class DocumentReferenceInput(BaseModel):
    id: UUID

class SubscriptionSource(BaseModel):
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str


class SubscriptionInput(BaseModel):
    source: SubscriptionSource
    context: Optional[str]


class PromptInput(BaseModel):
    prompt: str
    response: str
