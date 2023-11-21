import strawberry.federation as sb
import uuid
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

@sb.type
class SlackInstallation:
    id: uuid.UUID = sb.field()
    team_id: uuid.UUID = sb.field()
    slack_team_id: str = sb.field()
    bot_token: str = sb.field()

    @classmethod
    def from_orm(cls, orm: SlackInstallationOrm) -> "SlackInstallation":
        return SlackInstallation(
            id=orm.id,
            team_id=orm.team_id,
            slack_team_id=orm.slack_team_id,
            bot_token=orm.bot_token,
        )

@sb.input
class SlackInstallationInput:
    slack_team_id: str = sb.field()
