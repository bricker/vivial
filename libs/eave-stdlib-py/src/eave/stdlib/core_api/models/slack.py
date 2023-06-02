from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


import pydantic


class SlackInstallation(BaseResponseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str


class SlackInstallationInput(BaseInputModel):
    slack_team_id: str
