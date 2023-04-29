import eave.core.internal.orm.slack_installation
import eave.core.internal.database as eave_db
from eave.core.internal.orm.team import TeamOrm
import eave.stdlib.core_api.models as models
import eave.stdlib.core_api.operations as eave_ops
import fastapi


async def query(
    input: eave_ops.GetSlackInstallation.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetSlackInstallation.ResponseBody:
    async with eave_db.async_session.begin() as db_session:
        slack_installation = await eave.core.internal.orm.slack_installation.SlackInstallationOrm.one_or_exception(
            session=db_session,
            slack_team_id=input.slack_installation.slack_team_id,
        )

        team = await TeamOrm.one_or_exception(session=db_session, team_id=slack_installation.team_id)

        return eave_ops.GetSlackInstallation.ResponseBody(
            slack_installation=models.SlackInstallation.from_orm(slack_installation), team=models.Team.from_orm(team)
        )
