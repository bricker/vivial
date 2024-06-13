import enum

from eave.stdlib.core_api.models import BaseResponseModel


class AuthProvider(enum.StrEnum):
    google = "google"


class AuthenticatedAccount(BaseResponseModel):
    auth_provider: AuthProvider
    email: str | None
