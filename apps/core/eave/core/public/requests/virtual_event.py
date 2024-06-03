from asgiref.typing import HTTPScope
from eave.stdlib.core_api.models.virtual_event import VirtualEvent
from starlette.requests import Request
from starlette.responses import Response

import eave.stdlib.core_api.operations.virtual_event as ve
from eave.core.internal import database
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class GetMyVirtualEventsEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        body = await request.json()
        input = ve.GetMyVirtualEventsRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            team = await TeamOrm.one_or_exception(session=db_session, team_id=ensure_uuid(ctx.eave_authed_team_id))

            # TODO: some kind of fuzzy match or something
            vevents = await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    readable_name=input.query if input.query else None,
                    team_id=team.id,
                ),
            )

        bq_tables = EAVE_INTERNAL_BIGQUERY_CLIENT.list_tables(dataset_id=team.bq_dataset_id)
        virtual_events: list[VirtualEvent] = []

        for vevent in vevents:
            bq_table = next((bq_table for bq_table in bq_tables if bq_table.table_id == vevent.view_id), None)

            if bq_table:
                virtual_event = VirtualEvent(
                    id=vevent.id,
                    readable_name=vevent.readable_name,
                    description=vevent.description,
                    view_id=vevent.view_id,
                    fields=bq_table.
                )

        return json_response(
            ve.GetMyVirtualEventsRequest.ResponseBody(

            )
        )

class GetMyVirtualEventEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        body = await request.json()
        input = ve.GetMyVirtualEventRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            team = await TeamOrm.one_or_exception(session=db_session, team_id=ensure_uuid(ctx.eave_authed_team_id))

            vevent = await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    id=input.virtual_event.id,
                    team_id=team.id,
                ),
            )

        bq_tables = EAVE_INTERNAL_BIGQUERY_CLIENT.list_tables(dataset_id=team.bq_dataset_id)
        virtual_events: list[VirtualEvent] = []

        for vevent in vevents:
            bq_table = next((bq_table for bq_table in bq_tables if bq_table.table_id == vevent.view_id), None)

            if bq_table:
                virtual_event = VirtualEvent(
                    id=vevent.id,
                    readable_name=vevent.readable_name,
                    description=vevent.description,
                    view_id=vevent.view_id,
                    fields=bq_table.
                )

        return json_response(
            ve.GetMyVirtualEventsRequest.ResponseBody(

            )
        )
