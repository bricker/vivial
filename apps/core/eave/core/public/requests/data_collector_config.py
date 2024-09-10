from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.data_collector_config import DataCollectorConfigOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.data_collector_config import GetMyDataCollectorConfigRequest
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class GetMyDataCollectorConfigEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with database.async_session.begin() as db_session:
            config = await DataCollectorConfigOrm.one_or_exception(
                session=db_session, team_id=ensure_uuid(ctx.eave_authed_team_id)
            )

        return json_response(
            GetMyDataCollectorConfigRequest.ResponseBody(
                config=config.api_model,
            )
        )
