import uuid
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


import pydantic


class SlackInstallation(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str

class SlackInstallationPeek(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    slack_team_id: str


class SlackInstallationInput(BaseInputModel):
    slack_team_id: str
