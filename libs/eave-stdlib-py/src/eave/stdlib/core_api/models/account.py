import enum
import uuid
from collections.abc import Mapping
from typing import Any

from eave.stdlib.core_api.models import BaseResponseModel


class AuthProvider(enum.StrEnum):
    google = "google"


class AuthenticatedAccount(BaseResponseModel):
    auth_provider: AuthProvider
    email: str | None
