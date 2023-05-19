import http
from eave.stdlib import signing, eaveLogger
import eave.stdlib.core_api.client
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
from starlette.endpoints import HTTPEndpoint

from eave.stdlib.typing import LogContext
from .. import slack_app
from ..config import TASK_EXECUTION_COUNT_CONTEXT_KEY


# https://cloud.google.com/tasks/docs/creating-appengine-handlers
class SlackEventProcessorTask(HTTPEndpoint):
    _log_extra: LogContext
    _request: Request

    async def post(self, request: Request) -> Response:
        self._log_extra = {
            "json_fields": {
                "headers": dict(request.headers),
            }
        }

        self._request = request

        eaveLogger.info(
            "Request: POST /_tasks/slack-events",
            extra=self._log_extra,
        )

        default_success_response = Response(status_code=http.HTTPStatus.OK)

        is_valid_signature = await self._is_valid_signature()
        if is_valid_signature is not True:
            # Assume already logged
            return default_success_response  # Return success so Cloud Tasks doesn't retry

        task_execution_count = request.headers.get(GCP_GAE_TASK_EXECUTION_COUNT)
        handler = AsyncSlackRequestHandler(slack_app.app)
        response = await handler.handle(
            request,
            addition_context_properties={
                TASK_EXECUTION_COUNT_CONTEXT_KEY: task_execution_count,
            },
        )
        return response

    async def _is_valid_signature(self) -> bool:
        body = await self._request.body()
        signature = self._request.headers.get(EAVE_SIGNATURE_HEADER)
        request_id = self._request.headers.get(EAVE_REQUEST_ID_HEADER)
        origin_header = self._request.headers.get(EAVE_ORIGIN_HEADER)

        if not request_id or not origin_header or not signature:
            eaveLogger.warning("Missing required Eave header", extra=self._log_extra)
            return False

        try:
            origin = eave_origins.EaveOrigin(value=origin_header)
            signing_key = signing.get_key(origin)
        except (ValueError, KeyError):
            eaveLogger.warning(f"Invalid Eave origin: {origin_header}", extra=self._log_extra)
            return False

        signature_message = eave.stdlib.core_api.client.build_message_to_sign(
            method=self._request.scope["method"],
            origin=origin.value,
            request_id=request_id,
            url=self._request.scope["path"],
            payload=body.decode(),
            team_id=None,
            account_id=None,
        )
        try:
            eave.stdlib.signing.verify_signature_or_exception(
                signing_key=signing_key,
                message=signature_message,
                signature=signature,
            )
            return True
        except InvalidSignatureError:
            eaveLogger.warning("Invalid Eave signature", extra=self._log_extra)
            return False
