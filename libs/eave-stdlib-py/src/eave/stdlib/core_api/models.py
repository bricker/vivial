import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pydantic
from eave.stdlib.core_api.enums import (
    AuthProvider,
    DocumentPlatform,
    Integration,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)


class ConfluenceSpace(pydantic.BaseModel):
    key: str
    name: str

@dataclass
class AuthTokenPair:
    access_token: str
    refresh_token: str


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
    document_platform: Optional[DocumentPlatform]

    class Config:
        orm_mode = True


class AuthenticatedAccount(pydantic.BaseModel):
    id: uuid.UUID
    auth_provider: AuthProvider
    access_token: str

    class Config:
        orm_mode = True


class SlackInstallation(pydantic.BaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str

    class Config:
        orm_mode = True


class AtlassianInstallation(pydantic.BaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    atlassian_cloud_id: str
    confluence_space: Optional[str]
    available_confluence_spaces: Optional[List[ConfluenceSpace]]
    oauth_token_encoded: str

    class Config:
        orm_mode = True


class GithubInstallation(pydantic.BaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    github_install_id: str

    class Config:
        orm_mode = True


class Integrations(pydantic.BaseModel):
    """
    Key-value mapping of Integration to Installation info.
    The keys here will match the enum cases in enums.Integration
    """

    github: Optional[GithubInstallation]
    slack: Optional[SlackInstallation]
    atlassian: Optional[AtlassianInstallation]

class ErrorResponse(pydantic.BaseModel):
    eave_account_id: Optional[str]
    eave_origin: Optional[str]
    eave_team_id: Optional[str]
    request_id: Optional[str]
    request_method: Optional[str]
    request_scheme: Optional[str]
    request_path: Optional[str]
