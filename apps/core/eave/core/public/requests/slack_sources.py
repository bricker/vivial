import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import fastapi


async def query(
    input: eave_ops.GetSlackSource.RequestBody, request: fastapi.Request, response: fastapi.Response
) -> eave_ops.GetSlackSource.ResponseBody:
    # TODO: doing lookup by slack team id will reqruire adding an index on slack team id to db orm
    async with await eave_db.get_session() as session:
        slack_source = await eave_orm.SlackSource.one_or_none_by_slack_team_id(
            session=session,
            slack_team_id=input.slack_source.slack_team_id,
        )

        # TODO where should nullability be propogated to/handled?
        return eave_ops.GetSlackSource.ResponseBody(slack_source=slack_source)
