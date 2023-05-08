import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.core.public.request_state as eave_request_util
import eave.stdlib.core_api as eave_core

from starlette.responses import JSONResponse, Response
from starlette.requests import Request
import eave.stdlib.api_util as eave_api_util
from ..http_endpoint import HTTPEndpoint

class GetTeam(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave_request_util.get_eave_state(request=request)
        eave_team_orm = eave_state.eave_team

        async with eave_db.async_session.begin() as db_session:
            integrations = await eave_team_orm.get_integrations(session=db_session)

        eave_team = eave_core.models.Team.from_orm(eave_team_orm)

        return eave_api_util.json_response(eave_core.operations.GetTeam.ResponseBody(
            team=eave_team,
            integrations=integrations,
        ))
