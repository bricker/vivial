import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.stdlib import logger

from . import util as eave_request_util


async def query(
    input: eave_ops.GetSlackInstallation.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetSlackInstallation.ResponseBody:
    logger.debug("slack_source.query")
    await eave_request_util.validate_signature_or_fail(request=request)

    async with eave_db.get_async_session() as db_session:
        slack_installation = await eave_orm.SlackInstallationOrm.one_or_exception(
            session=db_session,
            slack_team_id=input.slack_installation.slack_team_id,
        )

        team = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=slack_installation.team_id)

        return eave_ops.GetSlackInstallation.ResponseBody(
            slack_installation=models.SlackInstallation.from_orm(slack_installation), team=models.Team.from_orm(team)
        )
