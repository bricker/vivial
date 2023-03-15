from datetime import datetime
from typing import Optional

from pydantic import UUID4, AnyHttpUrl, AnyUrl, BaseModel, EmailStr, HttpUrl

from eave.internal.orm import (
    AccessRequestOrm,
    DocumentReferenceOrm,
    SubscriptionOrm,
    TeamOrm,
)
from eave.public.shared import DocumentPlatform, SubscriptionSource


class DocumentReferencePublic(BaseModel):
    id: UUID4
    document_id: str
    document_url: str

    @classmethod
    def from_orm(cls, orm: DocumentReferenceOrm) -> "DocumentReferencePublic":
        return cls(
            id=orm.id,
            document_id=orm.document_id,
            document_url=orm.document_url,
        )


class SubscriptionPublic(BaseModel):
    id: UUID4
    source: SubscriptionSource
    document_reference_id: Optional[UUID4]

    @classmethod
    def from_orm(cls, orm: SubscriptionOrm) -> "SubscriptionPublic":
        return cls(
            id=orm.id,
            source=orm.source,
            document_reference_id=orm.document_reference_id,
        )


class AccessRequestPublic(BaseModel):
    id: UUID4
    visitor_id: Optional[UUID4]
    email: EmailStr
    created: datetime

    @classmethod
    def from_orm(cls, orm: AccessRequestOrm) -> "AccessRequestPublic":
        return cls(
            id=orm.id,
            visitor_id=orm.visitor_id,
            email=EmailStr(orm.email),
            created=orm.created,
        )


class TeamPublic(BaseModel):
    id: UUID4
    name: str
    document_platform: DocumentPlatform

    @classmethod
    def from_orm(cls, orm: TeamOrm) -> "TeamPublic":
        return cls(
            id=orm.id,
            name=orm.name,
            document_platform=orm.document_platform,
        )
