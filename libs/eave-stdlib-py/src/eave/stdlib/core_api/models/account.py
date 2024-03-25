import enum
import uuid
from typing import Any, Mapping, Optional

from eave.stdlib.core_api.models import BaseResponseModel


class AuthProvider(enum.StrEnum):
    google = "google"
    github = "github"


class AuthenticatedAccount(BaseResponseModel):
    id: uuid.UUID
    auth_provider: AuthProvider
    visitor_id: Optional[uuid.UUID]
    team_id: uuid.UUID
    opaque_utm_params: Optional[Mapping[str, Any]]
    email: Optional[str]


class AnalyticsAccount(BaseResponseModel):
    id: uuid.UUID
    auth_provider: AuthProvider
    visitor_id: Optional[uuid.UUID]
    team_id: uuid.UUID
    opaque_utm_params: Optional[Mapping[str, Any]]
