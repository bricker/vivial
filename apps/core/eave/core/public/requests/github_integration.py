import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
from eave.stdlib.http_endpoint import HTTPEndpoint


import eave.stdlib.api_util as eave_api_util
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.core_api.operations.github import GetGithubInstallation

from eave.stdlib.exceptions import NotFoundError


class GithubIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = GetGithubInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await eave_orm.GithubInstallationOrm.one_or_none(
                session=db_session,
                github_install_id=input.github_integration.github_install_id,
            )

            if not installation:
                raise NotFoundError()

            eave_team = await eave_orm.TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        return eave_api_util.json_response(
            GetGithubInstallation.ResponseBody(
                github_integration=installation.api_model,
                team=eave_team.api_model,
            )
        )
