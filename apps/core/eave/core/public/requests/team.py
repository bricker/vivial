import eave.stdlib
import eave.core.internal
import eave.core.public
from starlette.requests import Request
from starlette.responses import Response
import eave.stdlib.request_state
from eave.stdlib.core_api.operations.team import (
    GetTeam as GetTeamOp,
)

class GetTeam(eave.core.public.http_endpoint.HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave.stdlib.request_state.get_eave_state(request=request)

        async with eave.core.internal.database.async_session.begin() as db_session:
            eave_team_orm = await eave.core.internal.orm.TeamOrm.one_or_exception(
                session=db_session, team_id=eave.stdlib.util.unwrap(eave_state.eave_team_id)
            )

            integrations = await eave_team_orm.get_integrations(session=db_session)

        return eave.stdlib.api_util.json_response(
            GetTeamOp.ResponseBody(
                team=eave_team_orm.api_model,
                integrations=integrations,
            )
        )
