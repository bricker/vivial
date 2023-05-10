import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.core.public.request_state as eave_rutil
from eave.core.public.http_endpoint import HTTPEndpoint


import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response


class GithubIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_rutil.get_eave_state(request=request)
        body = await request.json()
        input = eave_core.operations.GetGithubInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.GithubInstallationOrm.one_or_exception(
                session=db_session,
                github_install_id=input.github_integration.github_install_id,
            )

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        eave_team = eave_core.models.Team.from_orm(eave_team)
        integration = eave_core.models.GithubInstallation.from_orm(installation)

        return eave_api_util.json_response(
            eave_core.operations.GetGithubInstallation.ResponseBody(
                github_integration=integration,
                team=eave_team,
            )
        )