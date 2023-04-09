import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.operations as eave_ops
import fastapi


async def query(
    input: eave_ops.GetSlackSource.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetSlackSource.ResponseBody:
    async with await eave_db.get_session() as session:
        slack_source = await eave_orm.SlackSource.one_or_none_by_slack_team_id(
            session=session,
            slack_team_id=input.slack_source.slack_team_id,
        )

        return eave_ops.GetSlackSource.ResponseBody(slack_source=slack_source)
