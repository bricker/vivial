import uuid
from typing import Optional
from eave.stdlib.core_api.models import BaseResponseModel


class MetabaseInstance(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    jwt_signing_key: Optional[str]
    route_id: Optional[uuid.UUID]
