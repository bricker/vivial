from typing import Optional, cast

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal import database
from eave.core.internal.bigquery.dbchanges import BigQueryTableHandle, DatabaseChangesTableHandle
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.stdlib.api_util import get_header_value_or_exception
from eave.stdlib.exceptions import ForbiddenError, UnauthorizedError
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.util import ensure_uuid
from eave.collectors.core.datastructures import DataIngestRequestBody, EventType


class DataIngestionEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = DataIngestRequestBody.from_json(data=body)

        http_scope = cast(HTTPScope, request.scope)

        # TODO: Move client credentials validation into middleware
        client_id = get_header_value_or_exception(scope=http_scope, name=EAVE_CLIENT_ID_HEADER)
        client_secret = get_header_value_or_exception(scope=http_scope, name=EAVE_CLIENT_SECRET_HEADER)

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

            await creds.touch(session=db_session)

        handle: Optional[BigQueryTableHandle] = None
        match input.event_type:
            case EventType.dbevent:
                handle = DatabaseChangesTableHandle(team_id=creds.team_id)

        if handle:
            await handle.insert(events=input.events)
        # TODO: is it worth sending back an error if we couldnt handle the event?

        response = Response(content="OK", status_code=200)
        return response
