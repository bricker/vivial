import http
from eave.stdlib.http_endpoint import HTTPEndpoint
import eave.stdlib.signing
from eave.stdlib.logging import eaveLogger
import eave.stdlib.requests
import eave.stdlib.eave_origins as eave_origins
from eave.stdlib.exceptions import InvalidSignatureError
from eave.stdlib.headers import (
    EAVE_ORIGIN_HEADER,
    EAVE_REQUEST_ID_HEADER,
    EAVE_SIGNATURE_HEADER,
    GCP_GAE_TASK_EXECUTION_COUNT,
)
import eave.stdlib.time
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.logging import LogContext
from .. import slack_app
from ..config import EAVE_CTX_KEY, TASK_EXECUTION_COUNT_CONTEXT_KEY


# https://cloud.google.com/tasks/docs/creating-appengine-handlers
class SlackEventProcessorTask(HTTPEndpoint):
    _ctx: LogContext
    _request: Request

    async def post(self, request: Request) -> Response:
        self._ctx = LogContext(request.scope)

        self._request = request

        eaveLogger.info(
            "Request: POST /_/slack/tasks/events",
            self._ctx,
        )

        task_execution_count = request.headers.get(GCP_GAE_TASK_EXECUTION_COUNT)
        self._ctx.set({TASK_EXECUTION_COUNT_CONTEXT_KEY: task_execution_count})

        handler = AsyncSlackRequestHandler(slack_app.app)
        response = await handler.handle(
            request,
            addition_context_properties={
                TASK_EXECUTION_COUNT_CONTEXT_KEY: task_execution_count,
                EAVE_CTX_KEY: self._ctx,
            },
        )

        return response
