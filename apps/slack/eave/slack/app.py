import http
from typing import cast
from slack_sdk.signature import SignatureVerifier
import eave.stdlib.api_util as eave_api_util
import eave.stdlib.core_api.client
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.logging
from eave.stdlib.task_queue import create_task_from_request
import eave.stdlib.time
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, Mount
from starlette.endpoints import HTTPEndpoint
from . import slack_app
from .config import app_config

eave.stdlib.time.set_utc()
eave.stdlib.logging.setup_logging()
eave.stdlib.core_api.client.set_origin(eave_origins.EaveOrigin.eave_slack_app)


class SlackEvent(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        success_response = Response(status_code=http.HTTPStatus.OK)

        # Verify the Slack signature, to avoid creating Tasks on the queue for invalid requests.
        verifier = SignatureVerifier(signing_secret=app_config.eave_slack_app_signing_secret)
        body = await request.body()
        headers = cast(
            dict[str, str], request.headers
        )  # request.headers is a Mapping which is_valid_request won't accept

        if not verifier.is_valid_request(body=body, headers=headers):
            return success_response

        await create_task_from_request(
            queue_name="slack-events-processor",
            target_path="/_ah/tasks/slack-events",
            request=request,
        )
        return success_response


class WarmupRequest(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        eave.stdlib.shared_config.preload()
        app_config.preload()
        return Response(status_code=http.HTTPStatus.OK, content="OK")


# https://cloud.google.com/tasks/docs/creating-appengine-handlers
class SlackEventProcessorTask(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        handler = AsyncSlackRequestHandler(slack_app.app)
        response = await handler.handle(request)
        return response


routes = [
    Route("/_ah/warmup", WarmupRequest, methods=["GET"]),
    Route("/_ah/tasks/slack-events", WarmupRequest, methods=["POST"]),
    Mount(
        "/slack",
        routes=[
            *eave_api_util.standard_endpoints_starlette,
            Route("/events", SlackEvent, methods=["POST"]),
            # Mount("/_tasks", routes=[
            #     Route("/process_slack_event", SlackEventProcessorTask, methods=["POST"]),
            # ]),
        ],
    ),
]

api = Starlette(routes=routes)
