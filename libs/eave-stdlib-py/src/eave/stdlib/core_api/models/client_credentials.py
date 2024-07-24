import uuid
from eave.stdlib.core_api.models import BaseResponseModel


class ClientCredentials(BaseResponseModel):
    id: uuid.UUID
    secret: str
    description: str | None
