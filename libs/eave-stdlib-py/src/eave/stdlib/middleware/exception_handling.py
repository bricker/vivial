import http
from typing import cast
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, ASGISendEvent, Scope
import starlette.types
from ..api_util import json_response

from ..logging import eaveLogger
from ..config import shared_config
from .base import EaveASGIMiddleware
from ..core_api.models.error import ErrorResponse


class ExceptionHandlingASGIMiddleware(EaveASGIMiddleware):
    """
    Although Starlette includes its own Exception handling middleware, it always re-raises the exception,
    which isn't the best when running on AppEngine, because AppEngine sends stderr messages to the Error Reporting API.
    """

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def _send(message: ASGISendEvent) -> None:
            nonlocal response_started, send

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, _send)
        except Exception as e:
            if shared_config.raise_app_exceptions:
                raise

            eave_state = self.eave_state(scope=scope)
            eaveLogger.exception(str(e), extra=eave_state.log_context)

            if not response_started:
                model = ErrorResponse(
                    status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    error_message=http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
                    context=eave_state.public_request_context,
                )

                response = json_response(model=model, status_code=model.status_code)
                await response(
                    cast(starlette.types.Scope, scope),
                    cast(starlette.types.Receive, receive),
                    cast(starlette.types.Send, send),
                )
