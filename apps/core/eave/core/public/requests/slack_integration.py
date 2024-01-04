from starlette.requests import Request
from starlette.responses import Response
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.core.internal.orm.team import TeamOrm
import eave.stdlib.api_util as eave_api_util
import eave.core.internal.database as eave_db
from eave.stdlib.core_api.operations.slack import GetSlackInstallation
from eave.stdlib.exceptions import NotFoundError

from eave.stdlib.http_endpoint import HTTPEndpoint


class SlackIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        """
        Raises an exception if no SlackInstallation can be found, or if there is
        a problem refreshing the SlackInstallation access tokens.
        """

        body = await request.json()
        input = GetSlackInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await SlackInstallationOrm.one_or_none(
                session=db_session,
                slack_team_id=input.slack_integration.slack_team_id,
            )

            if not installation:
                raise NotFoundError()

            # ensure access tokens are up to date
            await installation.refresh_token_or_exception(session=db_session)

            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        model = GetSlackInstallation.ResponseBody(
            slack_integration=installation.api_model,
            team=eave_team_orm.api_model,
        )

        return eave_api_util.json_response(model=model)
