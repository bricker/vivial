import uuid
from eave.stdlib.core_api.models import BaseResponseModel


class Outing(BaseResponseModel):
    id: uuid.UUID
    visitor_id: str
    account_id: uuid.UUID | None
    survey_id: uuid.UUID
