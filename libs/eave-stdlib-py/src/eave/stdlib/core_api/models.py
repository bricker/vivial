from datetime import datetime
from typing import Optional

import pydantic
from eave.stdlib.core_api.enums import (
    AuthProvider,
    DocumentPlatform,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)


class AuthInfo(pydantic.BaseModel):
    provider: AuthProvider
    id: str


# TODO: copy to ts stdlib
# TODO: change SupportedLink type name???
class SupportedLink(enum.Enum):
    """
    Link types that we support fetching content from for integration into AI documentation creation.
    """

    github = "github"


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


class Account(pydantic.BaseModel):
    auth_provider: AuthProvider


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


class AtlassianInstallation(pydantic.BaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    atlassian_cloud_id: str
    confluence_space: str
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
