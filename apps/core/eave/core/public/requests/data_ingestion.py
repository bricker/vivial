import aiohttp
from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.collectors.core.datastructures import DataIngestRequestBody, EventType
from eave.core.internal import database
from eave.core.internal.atoms.models.db_record_fields import GeoRecordField
from eave.core.internal.atoms.controllers.browser_events import BrowserEventsController
from eave.core.internal.atoms.controllers.db_events import DatabaseEventsController
from eave.core.internal.atoms.controllers.http_client_events import HttpClientEventsController
from eave.core.internal.atoms.controllers.http_server_events import HttpServerEventsController
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.api_util import get_header_value, get_header_value_or_exception
from eave.stdlib.exceptions import ForbiddenError, UnauthorizedError
from eave.stdlib.headers import EAVE_CLIENT_ID_HEADER, EAVE_CLIENT_SECRET_HEADER
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class BrowserDataIngestionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        # client_id = get_header_value_or_exception(scope=scope, name=EAVE_CLIENT_ID_HEADER)
        origin_header = get_header_value_or_exception(scope=scope, name=aiohttp.hdrs.ORIGIN)
        response = Response()

        # body = await request.json()
        client_id = request.query_params.get("clientId")

        if client_id is None:
            raise UnauthorizedError("missing clientId query param")

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
                raise ForbiddenError("invalid scope")

            eave_team = await TeamOrm.one_or_exception(session=db_session, team_id=creds.team_id)

            if not eave_team.origin_allowed(origin=origin_header):
                raise ForbiddenError("invalid origin")

            creds.touch(session=db_session)

        body = await request.json()
        input = DataIngestRequestBody.from_json(data=body)

        if (events := input.events.get(EventType.browser_event)) and len(events) > 0:
            # These headers are set by the GCP Load Balancer.
            # They will not be present during local development.
            geo_region = get_header_value(scope=scope, name="eave-lb-geo-region")
            geo_subdivision = get_header_value(scope=scope, name="eave-lb-geo-subdivision")
            geo_city = get_header_value(scope=scope, name="eave-lb-geo-city")
            geo_coordinates = get_header_value(scope=scope, name="eave-lb-geo-coordinates")
            client_ip = get_header_value(scope=scope, name="eave-lb-client-ip")

            if client_ip is None:
                client_attrs = scope["client"]
                if client_attrs is not None:
                    client_ip, _ = client_attrs

            geolocation = GeoRecordField(
                region=geo_region,
                subdivision=geo_subdivision,
                city=geo_city,
                coordinates=geo_coordinates,
            )

            handle = BrowserEventsController(client=creds)
            await handle.insert_with_geolocation(
                events=events,
                geolocation=geolocation,
                client_ip=client_ip,
                ctx=ctx,
            )

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

            creds.touch(session=db_session)

        if (db_events := input.events.get(EventType.db_event)) and len(db_events) > 0:
            handle = DatabaseEventsController(client=creds)
            await handle.insert(events=db_events, ctx=ctx)

        if (http_server_events := input.events.get(EventType.http_server_event)) and len(http_server_events) > 0:
            handle = HttpServerEventsController(client=creds)
            await handle.insert(events=http_server_events, ctx=ctx)

        if (http_client_events := input.events.get(EventType.http_client_event)) and len(http_client_events) > 0:
            handle = HttpClientEventsController(client=creds)
            await handle.insert(events=http_client_events, ctx=ctx)

        if (browser_events := input.events.get(EventType.browser_event)) and len(browser_events) > 0:
            handle = BrowserEventsController(client=creds)
            await handle.insert_with_geolocation(
                events=browser_events,
                geolocation=None,
                client_ip=None,
                ctx=ctx,
            )

        response = Response(status_code=200)
        return response
