from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

import eave.stdlib.core_api.operations.virtual_event as ve
from eave.core.internal import database
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.models.virtual_event import VirtualEventDetails, VirtualEventField, VirtualEventPeek
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext
from eave.stdlib.util import ensure_uuid


class ListMyVirtualEventsEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        body = await request.json()
        input = ve.ListMyVirtualEventsRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            # TODO: some kind of fuzzy match or something
            vevents = await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    readable_name=input.query if input.query else None,
                    team_id=ensure_uuid(ctx.eave_authed_team_id),
                ),
            )

        return json_response(
            ve.ListMyVirtualEventsRequest.ResponseBody(
                virtual_events=[VirtualEventPeek.from_orm(orm) for orm in vevents],
            )
        )


class GetMyVirtualEventDetailsEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        body = await request.json()
        input = ve.GetMyVirtualEventDetailsRequest.RequestBody.parse_obj(body)
        team_id = ensure_uuid(ctx.eave_authed_team_id)

        async with database.async_session.begin() as db_session:
            vevent = (
                await VirtualEventOrm.query(
                    session=db_session,
                    params=VirtualEventOrm.QueryParams(
                        id=input.virtual_event.id,
                        team_id=team_id,
                    ),
                )
            ).one()

        bq_table = EAVE_INTERNAL_BIGQUERY_CLIENT.get_table_or_exception(dataset_id=team_id.hex, table_id=vevent.view_id)

        return json_response(
            ve.GetMyVirtualEventDetailsRequest.ResponseBody(
                virtual_event=VirtualEventDetails(
                    id=vevent.id,
                    view_id=vevent.view_id,
                    readable_name=vevent.readable_name,
                    description=vevent.description,
                    fields=[VirtualEventField.from_bq_field(field) for field in bq_table.schema],
                ),
            )
        )
