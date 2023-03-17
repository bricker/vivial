from datetime import datetime
import enum
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

import pydantic

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


class AccessRequest(pydantic.BaseModel):
    id: pydantic.UUID4
    visitor_id: Optional[pydantic.UUID4]
    email: pydantic.EmailStr
    created: datetime

class DocumentReference(pydantic.BaseModel):
    id: pydantic.UUID4
    document_id: str
    document_url: str

class SubscriptionSource(pydantic.BaseModel):
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str

    @dataclass
    class Details:
        team: str
        channel: str
        ts: str

    @property
    def details(self) -> Details:
        team, channel, ts = self.id.split("#")
        return SubscriptionSource.Details(team=team, channel=channel, ts=ts)

class Subscription(pydantic.BaseModel):
    id: pydantic.UUID4
    document_reference_id: Optional[UUID]
    source: SubscriptionSource

class Team(pydantic.BaseModel):
    id: pydantic.UUID4
    name: str
    document_platform: DocumentPlatform
