import uuid
from datetime import datetime
from typing import List, Optional
from eave.stdlib.typing import JsonObject

import pydantic

from .. import enums
from ...typing import LogContext
from . import forge as forge
from .base import EaveBaseModel


class ConfluenceSpace(EaveBaseModel):
    key: str
    name: str


class DocumentReference(EaveBaseModel):
    id: pydantic.UUID4
    document_id: str
    document_url: str

    class Config:
        orm_mode = True


class DocumentSearchResult(EaveBaseModel):
    title: str
    url: str


class SubscriptionSource(EaveBaseModel):
    platform: enums.SubscriptionSourcePlatform
    event: enums.SubscriptionSourceEvent
    id: str


class Subscription(EaveBaseModel):
    id: pydantic.UUID4
    document_reference_id: Optional[pydantic.UUID4]
    source: SubscriptionSource

    class Config:
        orm_mode = True


class Team(EaveBaseModel):
    id: pydantic.UUID4
    name: str
    document_platform: Optional[enums.DocumentPlatform]
    beta_whitelisted: bool = False

    class Config:
        orm_mode = True


class AuthenticatedAccount(EaveBaseModel):
    id: uuid.UUID
    auth_provider: enums.AuthProvider
    visitor_id: Optional[uuid.UUID]
    team_id: uuid.UUID
    access_token: str

    class Config:
        orm_mode = True


class SlackInstallation(EaveBaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str

    class Config:
        orm_mode = True


class GithubInstallation(EaveBaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    github_install_id: str

    class Config:
        orm_mode = True


class Integrations(EaveBaseModel):
    """
    Key-value mapping of Integration to Installation info.
    The keys here will match the enum cases in enums.Integration
    """

    github: Optional[GithubInstallation]
    slack: Optional[SlackInstallation]
    forge: Optional[forge.ForgeInstallation]


class ErrorResponse(EaveBaseModel):
    status_code: int
    error_message: str
    context: Optional[JsonObject]
