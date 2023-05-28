import uuid
from typing import Optional
from eave.stdlib.typing import JsonObject

import pydantic

from .. import enums
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


class ErrorResponse(EaveBaseModel):
    status_code: int
    error_message: str
    context: Optional[JsonObject]
