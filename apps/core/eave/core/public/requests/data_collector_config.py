from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.data_collector_config import DataCollectorConfigOrm
from eave.stdlib.api_util import get_header_value_or_exception, json_response
from eave.stdlib.core_api.operations.data_collector_config import GetMyDataCollectorConfigRequest
from eave.stdlib.exceptions import ForbiddenError, UnauthorizedError
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class GetMyDataCollectorConfigEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        # TODO: Move client credentials validation into middleware
        client_id = get_header_value_or_exception(scope=scope, name=EAVE_CLIENT_ID_HEADER)
        client_secret = get_header_value_or_exception(scope=scope, name=EAVE_CLIENT_SECRET_HEADER)

        async with database.async_session.begin() as db_session:
            creds = (
                await ClientCredentialsOrm.query(
                    session=db_session,
                    params=ClientCredentialsOrm.QueryParams(
                        id=ensure_uuid(client_id),
                        secret=client_secret,
                    ),
                )
            ).one_or_none()

            if not creds:
                raise UnauthorizedError("invalid credentials")

            if not (creds.scope & ClientScope.write) > 0:
                raise ForbiddenError("invalid scopes")

            creds.touch(session=db_session)

        async with database.async_session.begin() as db_session:
            config = await DataCollectorConfigOrm.one_or_exception(
                session=db_session, team_id=ensure_uuid(creds.team_id)
            )

        return json_response(
            GetMyDataCollectorConfigRequest.ResponseBody(
                config=config.api_model,
            )
        )
