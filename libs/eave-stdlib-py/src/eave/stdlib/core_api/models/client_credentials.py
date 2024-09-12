import uuid
from datetime import datetime
from enum import StrEnum

from eave.stdlib.core_api.models import BaseResponseModel


class ClientCredentials(BaseResponseModel):
    id: uuid.UUID
    secret: str
    description: str | None
    last_used: datetime | None
    combined: str


class CredentialsAuthMethod(StrEnum):
    query_params = "query_params"
    headers = "headers"
