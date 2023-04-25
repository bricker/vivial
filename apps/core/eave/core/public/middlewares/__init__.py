import eave.stdlib.exceptions as eave_exceptions
import fastapi

from . import asgi_types


class EaveASGIMiddleware:
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: asgi_types.ASGIFramework

    def __init__(self, app: asgi_types.ASGIFramework) -> None:
        self.app = app

    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        try:
            await self.process(scope, receive, send)
        except fastapi.HTTPException as e:
            response = fastapi.Response(status_code=e.status_code)
            await response(scope, receive, send)  # type:ignore
            return
        except eave_exceptions.HTTPException as e:
            response = fastapi.Response(status_code=e.status_code)
            await response(scope, receive, send)  # type:ignore
            return

    async def process(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        ...
