import http
from typing import cast
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, ASGISendEvent, Scope
import starlette.types

from eave.stdlib.request_state import EaveRequestState
from ..api_util import json_response

from ..logging import eaveLogger
from ..config import SHARED_CONFIG
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
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, _send)
        except Exception as e:
            eave_state = EaveRequestState.load(scope=scope)
            eaveLogger.exception(e, eave_state.ctx)

            if SHARED_CONFIG.raise_app_exceptions:
                # NOTE: In development and test, this effectively converts every HTTPException into a 500 Server Error, and can make it difficult to troubleshoot request errors.
                # That isn't great. Something to fix when possible.
                raise

            if not response_started:
                # In production, all errors return a 500 as a security precaution for internal APIs.
                # For public APIs, more useful response codes will be returned, but there are currently no public APIs.
                model = ErrorResponse(
                    status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                    error_message=http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase,
                    context=eave_state.ctx.public,
                )

                response = json_response(model=model, status_code=model.status_code)
                await response(
                    cast(starlette.types.Scope, scope),
                    cast(starlette.types.Receive, receive),
                    cast(starlette.types.Send, send),
                )
