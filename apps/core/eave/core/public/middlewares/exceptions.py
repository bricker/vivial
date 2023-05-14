import eave.stdlib
import eave.core.public
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope
from starlette.responses import JSONResponse

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
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        eave_state = self.eave_state(scope=scope)

        try:
            await self.app(scope, receive, send)
        except eave.stdlib.exceptions.UnauthorizedError as e:
            eave.stdlib.logger.error(
                "Authentication error occurred. The client will be logged out.",
                exc_info=e,
                extra=eave_state.log_context,
            )

            body = eave.stdlib.core_api.models.ErrorResponse(
                status_code=e.status_code,
                error_message="authentication error",
                context=eave_state.public_request_context,
            )
            response = JSONResponse(status_code=e.status_code, content=body.json())
            eave.stdlib.cookies.delete_auth_cookies(response=response)
            await response(scope, receive, send)  # type:ignore
            return

        except eave.stdlib.exceptions.HTTPException as e:
            eave.stdlib.logger.error("Exception while processing middleware.", exc_info=e, extra=eave_state.log_context)

            body = eave.stdlib.core_api.models.ErrorResponse(
                status_code=e.status_code,
                error_message="unknown error",
                context=eave_state.public_request_context,
            )
            response = JSONResponse(status_code=e.status_code, content=body.json())
            await response(scope, receive, send)  # type:ignore
            return

        # Starlette's Exception middleware will handle all other exceptions.
