from enum import IntEnum
import uuid

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class TeamQueryInput(BaseInputModel):
    id: uuid.UUID


class DashboardAccess(IntEnum):
    DENY = 0
    ALLOW = 1


class Team(BaseResponseModel):
    id: uuid.UUID
    name: str
    dashboard_access: DashboardAccess
