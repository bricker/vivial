from starlette.requests import Request
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.team import TeamOrm
import eave.stdlib.api_util as eave_api_util
from starlette.responses import Response

import eave.core.internal.database as eave_db
from eave.stdlib.core_api.operations.atlassian import GetAtlassianInstallation
from eave.stdlib.exceptions import NotFoundError


from eave.stdlib.http_endpoint import HTTPEndpoint


class AtlassianIntegration(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = GetAtlassianInstallation.RequestBody.parse_obj(body)

        async with eave_db.async_session.begin() as db_session:
            installation = await AtlassianInstallationOrm.one_or_none(
                session=db_session,
                atlassian_cloud_id=input.atlassian_integration.atlassian_cloud_id,
            )

            if not installation:
                raise NotFoundError()

            eave_team = await TeamOrm.one_or_exception(
                session=db_session,
                team_id=installation.team_id,
            )

        return eave_api_util.json_response(
            GetAtlassianInstallation.ResponseBody(
                atlassian_integration=installation.api_model,
                team=eave_team.api_model,
            )
        )
