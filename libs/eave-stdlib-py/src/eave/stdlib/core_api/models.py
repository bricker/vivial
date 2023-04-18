import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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

    class Config:
        orm_mode = True


class DocumentReference(pydantic.BaseModel):
    id: pydantic.UUID4
    document_id: str
    document_url: str

    class Config:
        orm_mode = True


class SubscriptionSource(pydantic.BaseModel):
    platform: SubscriptionSourcePlatform
    event: SubscriptionSourceEvent
    id: str


class Subscription(pydantic.BaseModel):
    id: pydantic.UUID4
    document_reference_id: Optional[pydantic.UUID4]
    source: SubscriptionSource

    class Config:
        orm_mode = True


class Team(pydantic.BaseModel):
    id: pydantic.UUID4
    name: str
    document_platform: DocumentPlatform

    class Config:
        orm_mode = True


class SlackInstallation(pydantic.BaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str
    bot_id: str
    bot_user_id: Optional[str]

    class Config:
        orm_mode = True
