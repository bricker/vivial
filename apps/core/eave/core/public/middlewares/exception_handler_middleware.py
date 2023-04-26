import eave.stdlib.exceptions as eave_exceptions
import fastapi

from . import EaveASGIMiddleware, asgi_types


class ExceptionHandlerASGIMiddleware(EaveASGIMiddleware):
    """
    Handles custom Eave exceptions.
    Starlette already provides an Exception handling middleware, but this one is different in two ways:
    1. It specifically handles our custom exceptions,
    2. It starts at the _beginning_ of the middleware chain (that is, after Starlette's built-in ServerError middleware),
        so that we can catch and handle errors that occur in middlewares and respond appropriately.
    """

    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        try:
            await self.app(scope, receive, send)
        except eave_exceptions.HTTPException as e:
            response = fastapi.Response(status_code=e.status_code)
            await response(scope, receive, send)  # type:ignore
            return

        # Starlette's Exception middleware will handle all other exceptions.
