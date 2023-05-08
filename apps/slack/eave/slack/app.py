from typing import Any

import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api.client
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.logging
import eave.stdlib.time
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, Mount
from starlette.endpoints import HTTPEndpoint
from . import slack_app

eave.stdlib.time.set_utc()
eave.stdlib.logging.setup_logging()
eave.stdlib.core_api.client.set_origin(eave_origins.EaveOrigin.eave_slack_app)

class SlackEvent(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        handler = AsyncSlackRequestHandler(slack_app.app)
        response = await handler.handle(request)
        return response

# class SlackEventProcessorTask(HTTPEndpoint):
#     async def post(self, request: Request) -> Response:
#         pass

routes = [
    Mount("/slack", routes=[
        *eave_api_util.standard_endpoints,
        Route("/events", SlackEvent, methods=["POST"]),
        # Mount("/_tasks", routes=[
        #     Route("/process_slack_event", SlackEventProcessorTask, methods=["POST"]),
        # ]),
    ]),
]

api = Starlette(routes=routes)
