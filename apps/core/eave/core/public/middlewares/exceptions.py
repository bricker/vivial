from eave.stdlib.cookies import delete_auth_cookies
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.exceptions as eave_exceptions
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope
from eave.stdlib import logger
from starlette.responses import JSONResponse

import eave.core.public.request_state as request_util
import oauthlib.oauth2.rfc6749
from . import EaveASGIMiddleware


class ExceptionHandlerASGIMiddleware(EaveASGIMiddleware):
    """
    Handles custom Eave exceptions.
    Starlette already provides an Exception handling middleware, but this one is different in two ways:
    1. It specifically handles our custom exceptions,
    2. It starts at the _beginning_ of the middleware chain (that is, after Starlette's built-in ServerError middleware),
        so that we can catch and handle errors that occur in middlewares and respond appropriately.
    """

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        eave_state = request_util.get_eave_state(scope=scope)

        try:
            await self.app(scope, receive, send)
        except eave_exceptions.UnauthorizedError as e:
            logger.error("Authentication error occurred. The client will be logged out.", exc_info=e, extra=eave_state.log_context)

            body = eave_models.ErrorResponse(
                status_code=e.status_code,
                error_message="authentication error",
                context=eave_state.public_request_context,
            )
            response = JSONResponse(status_code=e.status_code, content=body.json())
            delete_auth_cookies(response=response)
            await response(scope, receive, send)  # type:ignore
            return

        except eave_exceptions.HTTPException as e:
            logger.error("Exception while processing middleware.", exc_info=e, extra=eave_state.log_context)

            body = eave_models.ErrorResponse(
                status_code=e.status_code,
                error_message="unknown error",
                context=eave_state.public_request_context,
            )
            response = JSONResponse(status_code=e.status_code, content=body.json())
            await response(scope, receive, send)  # type:ignore
            return

        # Starlette's Exception middleware will handle all other exceptions.
