import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as models
import eave.stdlib.core_api.operations as eave_ops
import fastapi
from eave.stdlib import logger

from . import util as eave_request_util


async def query(
    input: eave_ops.GetSlackSource.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetSlackSource.ResponseBody:
    logger.debug("subscriptions.delete_subscription")
    await eave_request_util.validate_signature_or_fail(request=request)

    async with await eave_db.get_session() as session:
        slack_source = await eave_orm.SlackSource.one_or_none_by_slack_team_id(
            session=session,
            slack_team_id=input.slack_source.slack_team_id,
        )

        if slack_source is not None:
            return eave_ops.GetSlackSource.ResponseBody(
                slack_source=models.SlackSource(
                    id=slack_source.id,
                    team_id=slack_source.team_id,
                    slack_team_id=slack_source.slack_team_id,
                    bot_token=slack_source.bot_token,
                    bot_id=slack_source.bot_id,
                    bot_user_id=slack_source.bot_user_id,
                )
            )
        return eave_ops.GetSlackSource.ResponseBody(slack_source=None)
