import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api as eave_core
from starlette.requests import Request
from starlette.responses import Response
from apps.core.eave.core.internal.orm.team import TeamOrm

import eave.core.internal.database as eave_db
import eave.stdlib.lib.request_state as eave_request_util

from ..http_endpoint import HTTPEndpoint


class GetTeam(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = eave_request_util.get_eave_state(request=request)

        async with eave_db.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session,
                team_id=eave_state.eave_team_id,
            )
            integrations = await eave_team_orm.get_integrations(session=db_session)

        eave_team = eave_core.models.Team.from_orm(eave_team_orm)

        return eave_api_util.json_response(
            eave_core.operations.GetTeam.ResponseBody(
                team=eave_team,
                integrations=integrations,
            )
        )
