import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.core.public.request_state as eave_rutil

from ..http_endpoint import HTTPEndpoint


class SlackIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.GetSlackInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.SlackInstallationOrm.one_or_exception(
                session=db_session,
                slack_team_id=input.slack_integration.slack_team_id,
            )

            eave_team_orm = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team_orm)
        integration = eave_core.models.SlackInstallation.from_orm(installation)

        model = eave_core.operations.GetSlackInstallation.ResponseBody(
            slack_integration=integration,
            team=eave_team,
        )

        return eave_api_util.json_response(model=model)



