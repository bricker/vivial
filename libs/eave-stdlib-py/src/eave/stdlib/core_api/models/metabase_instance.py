import uuid

from eave.stdlib.core_api.models import BaseResponseModel


class MetabaseInstance(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    jwt_signing_key: str | None
    route_id: uuid.UUID | None
