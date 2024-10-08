import datetime
import uuid
from eave.stdlib.core_api.models import BaseResponseModel


class Survey(BaseResponseModel):
    id: uuid.UUID
    visitor_id: str
    account_id: uuid.UUID | None
    start_time: datetime.datetime
    zip_codes: list[str]
    budget: int
    headcount: int
