import uuid
from eave.stdlib.core_api.models import BaseResponseModel


class MetabaseInstance(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
