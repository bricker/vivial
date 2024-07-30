from asgiref.typing import HTTPScope
from eave.stdlib.core_api.operations.client_credentials import GetMyClientCredentialsRequest
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class GetMyClientCredentialsEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with database.async_session.begin() as db_session:
            creds = await ClientCredentialsOrm.one_or_exception(
                session=db_session,
                params=ClientCredentialsOrm.QueryParams(team_id=ensure_uuid(ctx.eave_authed_team_id)),
            )
        return json_response(
            GetMyClientCredentialsRequest.ResponseBody(
                client_credentials=creds.api_model,
            )
        )
