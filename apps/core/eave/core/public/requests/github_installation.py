from http import HTTPStatus

from starlette.requests import Request
from starlette.responses import Response

import eave.core.internal.database as eave_db
import eave.stdlib.api_util as eave_api_util
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.operations.github_installation import DeleteGithubInstallation, QueryGithubInstallation
from eave.stdlib.exceptions import NotFoundError
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid, ensure_uuid_or_none


class QueryGithubInstallationEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = QueryGithubInstallation.RequestBody.parse_obj(body)
        github_install_id = input.github_installation.github_install_id if input.github_installation else None
        eave_team_id = input.team.id if input.team else None

        async with eave_db.async_session.begin() as db_session:
            installation = await GithubInstallationOrm.query(
                session=db_session,
                params=GithubInstallationOrm.QueryParams(
                    team_id=ensure_uuid_or_none(eave_team_id),
                    github_install_id=github_install_id,
                ),
            )

            if not installation:
                raise NotFoundError()

            if not installation.team_id:
                eave_team = None
            else:
                eave_team = await TeamOrm.one_or_exception(
                    session=db_session,
                    team_id=installation.team_id,
                )

        return eave_api_util.json_response(
            QueryGithubInstallation.ResponseBody(
                github_installation=installation.api_model,
                team=eave_team.api_model if eave_team else None,
            )
        )


class DeleteGithubInstallationEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = DeleteGithubInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            await GithubInstallationOrm.delete_by_github_install_id(
                session=db_session,
                team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                github_install_id=input.github_installation.github_install_id,
            )

        return Response(status_code=HTTPStatus.OK)
