import uuid

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class TeamQueryInput(BaseInputModel):
    id: uuid.UUID


class Team(BaseResponseModel):
    id: uuid.UUID
    name: str
