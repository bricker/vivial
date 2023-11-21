import strawberry.federation as sb
import enum
from eave.core.internal.orm.account import AccountOrm

from eave.stdlib.core_api.models import BaseResponseModel
import uuid
from typing import Any, Mapping, Optional

@sb.enum
class AuthProvider(enum.StrEnum):
    google = "google"
    slack = "slack"
    atlassian = "atlassian"
    github = "github"

@sb.type
class AuthenticatedAccount:
    id: uuid.UUID = sb.field()
    auth_provider: AuthProvider = sb.field()
    visitor_id: Optional[uuid.UUID] = sb.field()
    team_id: uuid.UUID = sb.field()
    opaque_utm_params: Optional[Mapping[str, Any]] = sb.field()
    email: Optional[str] = sb.field()

    @classmethod
    def from_orm(cls, orm: AccountOrm) -> "AuthenticatedAccount":
        return AuthenticatedAccount(
            id=orm.id,
            auth_provider=AuthProvider(value=orm.auth_provider),
            visitor_id=orm.visitor_id,
            team_id=orm.team_id,
            opaque_utm_params=orm.opaque_utm_params,
            email=orm.email,
        )

@sb.type
class AnalyticsAccount:
    id: uuid.UUID = sb.field()
    auth_provider: AuthProvider = sb.field()
    visitor_id: Optional[uuid.UUID] = sb.field()
    team_id: uuid.UUID = sb.field()
    opaque_utm_params: Optional[Mapping[str, Any]] = sb.field()
