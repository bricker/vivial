from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.collectors.core.datastructures import DataIngestRequestBody, EventType, LogIngestRequestBody
from eave.core.internal import database
from eave.core.internal.atoms.controllers.browser_events import BrowserEventsController
from eave.core.internal.atoms.controllers.collector_logs import AtomCollectorLogsController
from eave.core.internal.atoms.controllers.db_events import DatabaseEventsController
from eave.core.internal.atoms.controllers.http_client_events import HttpClientEventsController
from eave.core.internal.atoms.controllers.http_server_events import HttpServerEventsController
from eave.core.internal.atoms.controllers.openai_chat_completion import OpenAIChatCompletionController
from eave.core.internal.atoms.models.db_record_fields import GeoRecordField
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm
from eave.stdlib.api_util import get_header_value
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class BrowserDataIngestionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        response = Response()

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

            async with database.async_session.begin() as db_session:
                creds = await ClientCredentialsOrm.one_or_exception(
                    session=db_session,
                    params=ClientCredentialsOrm.QueryParams(
                        id=ensure_uuid(ctx.eave_client_id),
                        team_id=ensure_uuid(ctx.eave_authed_team_id),
                    ),
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

        async with database.async_session.begin() as db_session:
            creds = await ClientCredentialsOrm.one_or_exception(
                session=db_session,
                params=ClientCredentialsOrm.QueryParams(
                    id=ensure_uuid(ctx.eave_client_id),
                    team_id=ensure_uuid(ctx.eave_authed_team_id),
                ),
            )

        db_events = input.events.get(EventType.db_event)
        if db_events and len(db_events) > 0:
            handle = DatabaseEventsController(client=creds)
            await handle.insert(events=db_events, ctx=ctx)

        openai_chat_completion_events = input.events.get(EventType.openai_chat_completion)
        if openai_chat_completion_events and len(openai_chat_completion_events) > 0:
            handle = OpenAIChatCompletionController(client=creds)
            await handle.insert(events=openai_chat_completion_events, ctx=ctx)

        http_server_events = input.events.get(EventType.http_server_event)
        if http_server_events and len(http_server_events) > 0:
            handle = HttpServerEventsController(client=creds)
            await handle.insert(events=http_server_events, ctx=ctx)

        http_client_events = input.events.get(EventType.http_client_event)
        if http_client_events and len(http_client_events) > 0:
            handle = HttpClientEventsController(client=creds)
            await handle.insert(events=http_client_events, ctx=ctx)

        browser_events = input.events.get(EventType.browser_event)
        if browser_events and len(browser_events) > 0:
            handle = BrowserEventsController(client=creds)
            await handle.insert_with_geolocation(
                events=browser_events,
                geolocation=None,
                client_ip=None,
                ctx=ctx,
            )

        response = Response(status_code=200)
        return response


class LogDataIngestionEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        body = await request.json()
        input = LogIngestRequestBody.from_json(data=body)

        if input.logs:
            async with database.async_session.begin() as db_session:
                creds = await ClientCredentialsOrm.one_or_exception(
                    session=db_session,
                    params=ClientCredentialsOrm.QueryParams(
                        id=ensure_uuid(ctx.eave_client_id),
                        team_id=ensure_uuid(ctx.eave_authed_team_id),
                    ),
                )
            handle = AtomCollectorLogsController(client=creds)
            await handle.insert(
                raw_logs=input.logs,
                ctx=ctx,
            )

        response = Response(status_code=200)
        return response
