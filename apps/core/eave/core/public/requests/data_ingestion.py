from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.collectors.core.datastructures import DataIngestRequestBody, EventType
from eave.core.internal import database
from eave.core.internal.atoms.browser_events import BrowserEventsTableHandle
from eave.core.internal.atoms.db_events import DatabaseEventsTableHandle
from eave.core.internal.atoms.http_client_events import HttpClientEventsTableHandle
from eave.core.internal.atoms.http_server_events import HttpServerEventsTableHandle
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.api_util import get_header_value_or_exception
from eave.stdlib.exceptions import ForbiddenError, UnauthorizedError
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class BrowserDataIngestionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        # client_id = get_header_value_or_exception(scope=scope, name=EAVE_CLIENT_ID_HEADER)
        # origin_header = get_header_value_or_exception(scope=scope, name=aiohttp.hdrs.ORIGIN)

        # body = await request.json()
        qp = request.query_params._dict  # noqa: SLF001
        print(qp)
        client_id = qp["eaveClientId"]

        body = {"events": {"browser_event": [{**qp}]}}

        input = DataIngestRequestBody.from_json(data=body)

        async with database.async_session.begin() as db_session:
            creds = (
                await ClientCredentialsOrm.query(
                    session=db_session,
                    params=ClientCredentialsOrm.QueryParams(
                        id=ensure_uuid(client_id),
                    ),
                )
            ).one_or_none()

            if not creds:
                raise UnauthorizedError("invalid credentials")

            if not (creds.scope & ClientScope.write) > 0:
                raise ForbiddenError("invalid scopes")

            eave_team = await TeamOrm.one_or_exception(session=db_session, team_id=creds.team_id)

            # if origin_header not in eave_team.allowed_origins:
            #     raise ForbiddenError("Invalid origin")

            await creds.touch(session=db_session)

        if (events := input.events.get(EventType.browser_event)) and len(events) > 0:
            handle = BrowserEventsTableHandle(team=eave_team)
            await handle.insert(events=events)

        # Throw an error if there are any other event types in the payload?

        response = Response(status_code=200)
        return response


class ServerDataIngestionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        body = await request.json()
        input = DataIngestRequestBody.from_json(data=body)

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

            await creds.touch(session=db_session)

            eave_team = await TeamOrm.one_or_exception(session=db_session, team_id=creds.team_id)

        if (events := input.events.get(EventType.db_event)) and len(events) > 0:
            handle = DatabaseEventsTableHandle(team=eave_team)
            await handle.insert(events=events)

        if (events := input.events.get(EventType.http_server_event)) and len(events) > 0:
            handle = HttpServerEventsTableHandle(team=eave_team)
            await handle.insert(events=events)

        if (events := input.events.get(EventType.http_client_event)) and len(events) > 0:
            handle = HttpClientEventsTableHandle(team=eave_team)
            await handle.insert(events=events)

        if (events := input.events.get(EventType.browser_event)) and len(events) > 0:
            handle = BrowserEventsTableHandle(team=eave_team)
            await handle.insert(events=events)

        response = Response(status_code=200)
        return response
