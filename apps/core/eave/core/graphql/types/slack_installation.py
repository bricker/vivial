from typing import Optional
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

class SlackInstallationResolvers:
    @staticmethod
    def get_slack_installation(query: SlackInstallationInput) -> Optional[SlackInstallation]:
        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.SlackInstallationOrm.one_or_none(
                session=db_session,
                slack_team_id=input.slack_integration.slack_team_id,
            )

            if not installation:
                raise NotFoundError()

            # ensure access tokens are up to date
            await installation.refresh_token_or_exception(session=db_session)

            eave_team_orm = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        model = GetSlackInstallation.ResponseBody(
            slack_integration=installation.api_model,
            team=eave_team_orm.api_model,
        )

        return eave_api_util.json_response(model=model)

    @staticmethod
    def get_slack_installation_for_team(team_id: uuid.UUID) -> Optional[SlackInstallation]:
        ...