from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.team import (
    GetMyTeamRequest,
)
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import unwrap


class GetMyTeamEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with database.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(session=db_session, team_id=unwrap(ctx.eave_authed_team_id))

        return json_response(
            GetMyTeamRequest.ResponseBody(
                team=eave_team_orm.api_model,
            )
        )
