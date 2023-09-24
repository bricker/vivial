import strawberry
import uuid
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

@strawberry.type
class SlackInstallation:
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str

@strawberry.type
class SlackInstallationPeek:
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    slack_team_id: str

@strawberry.input
class SlackInstallationInput:
    slack_team_id: str
