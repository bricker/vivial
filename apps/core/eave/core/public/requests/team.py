from eave.core.internal import database
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.team import (
    GetTeamRequest,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import unwrap


class GetTeamEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)

        async with database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session, team_id=unwrap(eave_state.ctx.eave_team_id)
            )

        return json_response(
            GetTeamRequest.ResponseBody(
                team=eave_team_orm.api_model,
            )
        )
