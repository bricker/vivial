import enum

from eave.stdlib.core_api.models import BaseResponseModel
import uuid
from typing import Optional


class AuthProvider(enum.StrEnum):
    google = "google"
    slack = "slack"
    atlassian = "atlassian"
    github = "github"


class AuthenticatedAccount(BaseResponseModel):
    id: uuid.UUID
    auth_provider: AuthProvider
    visitor_id: Optional[uuid.UUID]
    team_id: uuid.UUID
    access_token: str