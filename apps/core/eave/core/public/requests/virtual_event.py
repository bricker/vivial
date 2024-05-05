from typing import override
from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

import eave.stdlib.core_api.operations.virtual_event as ve
from eave.core.internal import database
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.api_util import json_response
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid


class GetVirtualEventsEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, state: EaveRequestState) -> Response:
        body = await request.json()
        input = ve.GetMyVirtualEventsRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            # TODO: some kind of fuzzy match or something
            vevents = await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    readable_name=input.virtual_events.search_term if input.virtual_events else None,
                    team_id=ensure_uuid(state.ctx.eave_team_id),
                ),
            )

        return json_response(
            ve.GetMyVirtualEventsRequest.ResponseBody(
                virtual_events=[orm.api_model for orm in vevents],
            )
        )
