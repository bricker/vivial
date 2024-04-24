import enum
import uuid
from collections.abc import Mapping
from typing import Any

from eave.stdlib.core_api.models import BaseResponseModel


class AuthProvider(enum.StrEnum):
    google = "google"
    github = "github"


class AuthenticatedAccount(BaseResponseModel):
    id: uuid.UUID
    auth_provider: AuthProvider
    visitor_id: uuid.UUID | None
    team_id: uuid.UUID
    opaque_utm_params: Mapping[str, Any] | None
    email: str | None


class AnalyticsAccount(BaseResponseModel):
    id: uuid.UUID
    auth_provider: AuthProvider
    visitor_id: uuid.UUID | None
    team_id: uuid.UUID
    opaque_utm_params: Mapping[str, Any] | None
